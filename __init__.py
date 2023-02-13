# Card Timer
#
# Copyright (C) 2023  Sachin Govind
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from aqt import mw
from aqt.qt import *
from aqt.webview import WebContent
from aqt.toolbar import Toolbar, TopToolbar
from aqt.gui_hooks import webview_will_set_content, top_toolbar_did_init_links, reviewer_did_answer_card, review_did_undo, deck_browser_did_render, webview_did_receive_js_message, collection_did_load
from typing import Any, List
from bs4 import BeautifulSoup
from aqt.utils import tooltip
from anki.collection import Collection

config = mw.addonManager.getConfig(__name__)


class CardTimer():
    def __init__(self, mw):
        self.mw = mw
        if self.mw is None:
            return

        self.mw.addonManager.setWebExports(__name__, r"web/.*")
        self.packageName = mw.addonManager.addonFromModule(__name__)

        self.topToolbar: Toolbar = None
        self._initHooks()
        self.startCountingReviewsSince = 0

    def collection(self):
        collection = self.mw
        if collection is None:
            raise Exception('collection is not available')

        return collection

    def _createTimerElement(self):
        return """
			<span class="hitem" style="vertical-align: middle; padding-left: 0px">
                <table>
                    <tr id="cardTimerElement">
                        <td id="leftTimerButtons">
                            <button id="timerStartButton" onclick="startTimer()" class="startButton">Start</button>
                            <button id="playPauseButton" onclick="toggleRunning()" class="timerButton"
                                style="display: none;"></button>
                        </td>
                        <td id="timerCounts" class="progressValues">
                            <div>
                                <input id="numCardsField" type="number" min="0" max="9999" placeholder="# Cards" 
                                    class="progressValues" onblur="autoComputeTimeForTimer()"></input>
                            </div>
                            <div>
                                <input id="numSecsField" type="number" min="0" max="7200" placeholder="Time (s)"
                                    class="progressValues" onblur="roundEnteredTime()"></input>
                            </div>
                            <div id="cardCountElement" style="display: none;" class="progressValues" style="width: 95px;">
                                <span id="cardsDone" class="proportionDone"></span>
                                <span id="cardString" class="proportionDone" style="padding-left: 2px"></span>
                            </div>
                            <div id="timeElement" style="display: none;" class="progressValues" style="width: 95px;">
                                <span id="timeDone" class="proportionDone"></span>
                                <span id="timeString" class="proportionDone" style="padding-left: 2px"></span>
                            </div>
                        </td>
                        <td id="rightTimerButtons">
                            <button id="resetButton" class="timerButton" onclick="resetTimer()" style="display: none;">🔃</button>
                        </td>
                    </tr>
                </table>
            </span>
		"""

    def _onWebviewWillSetContent(self, content: WebContent, context: Union[Any, TopToolbar]):
        if not isinstance(context, TopToolbar):
            return

        content.css.append(f"/_addons/{self.packageName}/web/cardTimer.css")
        content.js.append(f"/_addons/{self.packageName}/web/cardTimer.js")

    def _onTopToolbarDidInitLinks(self, links: List[str], toolbar: Toolbar):
        links.append(self._createTimerElement())
        self.topToolbar = toolbar

    def _updateTimerElement(self):
        if self.topToolbar is None:
            return

        cardsSinceTimeStart = self._getCardsStudiedSinceTimerStarted()
        if str(cardsSinceTimeStart).isnumeric():
            cardsSinceTimeStart = int(cardsSinceTimeStart)

        self.topToolbar.web.eval(
            """
				setCards(%s);
			""" % cardsSinceTimeStart
        )

    def _getCardsStudiedSinceTimerStarted(self):
        cardsStudied = self.mw.col.db.scalar("""
			select count(r.id) from revlog as r
			where r.id > %s
		""" % self.startCountingReviewsSince)

        if cardsStudied == None:
            cardsStudied = 0

        return cardsStudied

    def _reviewerAnswered(self, reviewer, card, ease):
        self._updateTimerElement()

    def _reviewerUndid(self, cardId):
        self._updateTimerElement()

    def _deckBrowserRendered(self, db):
        self._updateTimerElement()

    def _handleTimerStateChangeMessage(self, handled, cmd: str, context):
        if not isinstance(context, TopToolbar):
            return handled

        if cmd.startswith("cardTimerStart"):
            self.startCountingReviewsSince = self.mw.col.db.scalar("""
				select r.id from revlog as r
				order by r.id desc
				limit 1
			""")
            if self.startCountingReviewsSince == None:
                self.startCountingReviewsSince = 0
            self._updateTimerElement()
            return (True, None)

        return handled

    def _computeAverageTime(self, col: Collection):
        mostRecentTimes = col.db.list("""
            select id from revlog as r
            order by id desc 
            limit 1000
        """)

        avgTime = 8
        if len(mostRecentTimes) > 0:
            # compute time per card
            times = []
            for idx in range(0, len(mostRecentTimes) - 1):
                time = mostRecentTimes[idx] - \
                    mostRecentTimes[idx + 1]  # in reverse order
                if time < 60000:
                    times.append(time)

            avgTime = (sum(times) / len(times)) / 1000

        self.topToolbar.web.eval("""
            setAverageDurationPerCard(%s)
        """ % 8)  # % avgTime)

    def _initHooks(self):
        webview_will_set_content.append(self._onWebviewWillSetContent)
        top_toolbar_did_init_links.append(self._onTopToolbarDidInitLinks)
        reviewer_did_answer_card.append(self._reviewerAnswered)
        review_did_undo.append(self._reviewerUndid)
        deck_browser_did_render.append(self._deckBrowserRendered)
        collection_did_load.append(self._computeAverageTime)
        webview_did_receive_js_message.append(
            self._handleTimerStateChangeMessage)


cardTimer = CardTimer(mw)
