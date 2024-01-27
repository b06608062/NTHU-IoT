$(document).ready(function () {
  $("#autoSend").hide();
  $('input[name="sendMode"]').change(function () {
    if ($('input[name="sendMode"]:checked').val() === "auto") {
      $("#manualSend").hide();
      $("#autoSend").show();
    } else {
      $("#autoSend").hide();
      $("#manualSend").show();
      stopAutoSend();
    }
  });
  $("#toggleAutoSend").click(function () {
    toggleAutoSend();
  });
  $("#floorRange").on("input", function () {
    $("#floorLabel").text("Select Floor: " + $(this).val());
  });
});

function sendData() {
  var data = $("#dataInput").val().trim();
  if (isAutoSending) {
    data = "Default data";
  } else if (!isAutoSending && data === "") {
    showNotification("No data to send", "error");
    return;
  }

  var floor = $("#floorRange").val();
  var mode = $('input[name="mode"]:checked').val();
  var data_rate_mode = $("#dataRateModeSwitch").is(":checked");

  var payload = {
    data: data,
    coordinates: { latitude, longitude },
    floor: floor,
    mode: mode,
    data_rate_mode: data_rate_mode,
  };

  $.ajax({
    url: "/send",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(payload),
    success: function (response) {
      showNotification("Success: " + response.message, "success");
      $("#log").append(
        "<div class='success-message'>[" +
          new Date().toLocaleTimeString() +
          "] Success: " +
          response.message +
          "</div>"
      );
    },
    error: function (xhr) {
      var errorMessage =
        xhr.responseJSON && xhr.responseJSON.message
          ? xhr.responseJSON.message
          : "An unknown error occurred";
      showNotification("Error: " + errorMessage, "error");
      $("#log").append(
        "<div class='error-message'>[" +
          new Date().toLocaleTimeString() +
          "] Error: " +
          errorMessage +
          "</div>"
      );
    },
  });

  $("#dataInput").val("");
}

function handleKeyPress(event) {
  if (event.key === "Enter") {
    sendData();
  }
}

var autoSendInterval;
var countdownInterval;
var isAutoSending = false;
function toggleAutoSend() {
  if (isAutoSending) {
    clearInterval(autoSendInterval);
    clearInterval(countdownInterval);
    isAutoSending = false;
    $("#toggleAutoSend")
      .text("Start Auto Send")
      .removeClass("btn-danger")
      .addClass("btn-success");
  } else {
    var intervalSeconds = parseInt($("#intervalInput").val());
    if (isNaN(intervalSeconds) || intervalSeconds < 5) {
      alert("Please enter a valid interval (seconds >= 5).");
      return;
    }
    isAutoSending = true;
    autoSendInterval = setInterval(sendData, intervalSeconds * 1000);
    countdown(intervalSeconds);
    $("#toggleAutoSend").removeClass("btn-success").addClass("btn-danger");
  }
}

function countdown(seconds) {
  updateButton(seconds);
  countdownInterval = setInterval(function () {
    seconds--;
    updateButton(seconds);
    if (seconds <= 0) {
      seconds = parseInt($("#intervalInput").val());
    }
  }, 1000);
}

function updateButton(seconds) {
  var buttonText = isAutoSending
    ? "Stop Auto Send (" + seconds + "s)"
    : "Start Auto Send";
  $("#toggleAutoSend").text(buttonText);
}

function stopAutoSend() {
  if (autoSendInterval) {
    clearInterval(autoSendInterval);
    clearInterval(countdownInterval);
    autoSendInterval = null;
    isAutoSending = false;
    $("#toggleAutoSend")
      .text("Start Auto Send")
      .removeClass("btn-danger")
      .addClass("btn-success");
  }
}

function showNotification(message, type) {
  var notification = $("<div>")
    .addClass("notification")
    .addClass(
      type === "success" ? "notification-success" : "notification-error"
    );
  var icon =
    type === "success"
      ? $("<i>").addClass("notification-icon fas fa-check-circle")
      : $("<i>").addClass("notification-icon fas fa-exclamation-circle");
  var content = $("<span>").addClass("notification-content").text(message);
  notification.append(icon).append(content);
  $("body").prepend(notification);
  notification.addClass("notification-slide-in");
  notification
    .slideDown(500)
    .delay(1000)
    .slideUp(500, function () {
      $(this).remove();
    });
}

var map;
var marker;
var latitude;
var longitude;
function initMap() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (position) {
        var pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        latitude = position.coords.latitude;
        longitude = position.coords.longitude;
        $("#lat-span").text(latitude);
        $("#lng-span").text(longitude);

        map = new google.maps.Map($("#map")[0], {
          center: pos,
          zoom: 18,
          draggableCursor: "default",
          clickableIcons: false,
        });

        marker = new google.maps.Marker({
          position: pos,
          map: map,
          title: "Your location",
        });

        map.addListener("click", function (e) {
          placeMarkerAndPanTo(e.latLng, map);
        });
      },
      function () {
        console.error("Geolocation failed: " + error.message);
      }
    );
  } else {
    console.error("Browser doesn't support geolocation.");
  }
}

function placeMarkerAndPanTo(latLng, map) {
  marker.setPosition(latLng);
  latitude = latLng.lat();
  longitude = latLng.lng();
  $("#lat-span").text(latitude);
  $("#lng-span").text(longitude);
  map.panTo(latLng);
}
