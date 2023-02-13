const cardTimerData = { duration: 0, timeElapsed: 0, isRunning: false, cardGoal: 0 }
const currentTime = () => Math.round(new Date().getTime() / 1000);
let avgDurationPerCard = 8;
var cardsDone = 0;

//TODO: use the strategy here: https://stackoverflow.com/questions/16134997/how-to-pause-and-resume-a-javascript-timer
//this will ensure accurate timing

function setAverageDurationPerCard(duration) {
	if (duration > 0) {
		avgDurationPerCard = duration;
	}
}

function startTimer() {
	const numSecsField = document.getElementById("numSecsField");
	const numCardsField = document.getElementById("numCardsField");
	if (!numSecsField || !numCardsField || numSecsField.value == "" || numCardsField.value == "") {
		return;
	}

	var duration = +(numSecsField.value);
	var cardGoal = +(numCardsField.value);
	if (duration < 0) {
		duration = 0;
		document.getElementById("numSecsField").value = 0;
	}
	if (duration > 7200) {
		duration = 7200;
		document.getElementById("numSecsField").value = 7200;
	}
	if (cardGoal < 0) {
		cardGoal = 0;
		document.getElementById("numCardsField").value = 0;
	}
	if (cardGoal > 9999) {
		cardGoal = 9999;
		document.getElementById("numCardsField").value = 9999;
	}

	setCards(0);
	cardTimerData.cardGoal = cardGoal || 0;
	cardTimerData.isRunning = true;
	cardTimerData.duration = duration;
	cardTimerData.timeElapsed = 0;
	setTimeElapsed(0);
	document.getElementById("playPauseButton").textContent = "⏸️";

	//now hide the start button and entry fields, and show the play/pause button, the progress bars, and the reset button
	document.getElementById("timerStartButton").style.display = "none";
	document.getElementById("numCardsField").style.display = "none";
	document.getElementById("numSecsField").style.display = "none";
	document.getElementById("cardCountElement").style.display = "";
	document.getElementById("timeElement").style.display = "";
	document.getElementById("playPauseButton").style.display = "";
	document.getElementById("resetButton").style.display = "";
	pycmd("cardTimerStart")
}

function toggleRunning() {
	cardTimerData.isRunning = !cardTimerData.isRunning;
	document.getElementById("playPauseButton").textContent = cardTimerData.isRunning ? "⏸️" : "▶️";
}

function resetTimer() {
	cardTimerData.isRunning = false;
	cardTimerData.duration = 0;
	cardTimerData.timeElapsed = 0;
	setCards(0);
	document.getElementById("timerStartButton").style.display = "";
	document.getElementById("numCardsField").style.display = "";
	document.getElementById("numSecsField").style.display = "";
	document.getElementById("cardCountElement").style.display = "none";
	document.getElementById("timeElement").style.display = "none";
	document.getElementById("playPauseButton").style.display = "none";
	document.getElementById("resetButton").style.display = "none";
}

function setTimeElapsed(time) {
	const leftPadWithSpaces = (per) => (new String(Math.round(100 * per))).padStart(3);

	var timeStringElement = document.getElementById("timeString");
	const duration = cardTimerData.duration;

	var proportion = 0;
	if (duration > 0) {
		proportion = time / duration;
	}
	if (proportion > 1) {
		proportion = 1;
	}

	var percentage = leftPadWithSpaces(proportion) + "%";
	var deficit = Math.round(time - cardsDone * avgDurationPerCard);
	var deficitString = "";
	if (deficit < 0) {
		deficitString = "(" + deficit + ")";
	} else {
		deficitString = "(+" + deficit + ")";
	}

	timeStringElement.innerText = time + " / " + duration + " s " + deficitString;
}

function setCards(cards) {
	cardsDone = cards;

	const leftPadWithSpaces = (per) => (new String(Math.round(100 * per))).padStart(3);
	var cardsStringElement = document.getElementById("cardString");

	var proportion = 0;
	if (cardTimerData.cardGoal > 0) {
		proportion = cards / cardTimerData.cardGoal;
	}
	if (proportion > 1) {
		proportion = 1
	}
	var percentage = leftPadWithSpaces(proportion) + "%";
	cardsStringElement.innerText = cards + " / " + (cardTimerData.cardGoal) + " cards";
}

function roundEnteredTime() {
	const numSecsField = document.getElementById("numSecsField");
	if (numSecsField.value > 0) {
		numSecsField.value = Math.round(numSecsField.value);
	} else if (numSecsField.value < 0) {
		numSecsField.value = 0;
	}
}

function autoComputeTimeForTimer() {
	const numCardsField = document.getElementById("numCardsField");
	if (numCardsField.value > 0) {
		numCardsField.value = Math.round(numCardsField.value);
	} else if (numCardsField.value < 0) {
		numCardsField.value = 0;
	}

	var enteredCards = numCardsField.value
	var secs = 0;
	if (enteredCards > 0) {
		secs = Math.round(enteredCards * avgDurationPerCard);
	}
	document.getElementById("numSecsField").value = secs;
}

setInterval(function () {
	if (cardTimerData.isRunning) {
		cardTimerData.timeElapsed += 1;
		setTimeElapsed(cardTimerData.timeElapsed);
	}
}, 1000);