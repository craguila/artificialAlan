@startTimer = (endtime) ->
  if window.countdown
    clearInterval window.countdown
  timerBox = document.getElementById('slides-timer')
  endtime = new Date(endtime)
  window.countdown = setInterval((->
    if endtime > new Date()
      minutos = Math.floor(((endtime - new Date())/1000)/60,0)
      segundos = Math.abs(Math.floor(((endtime - new Date())/1000)%60,0))
      if segundos < 10
        segundos = "0"+segundos
      timerBox.innerHTML = minutos + ":" + segundos
    else
      minutos = Math.floor(((new Date()- endtime)/1000)/60,0)
      segundos = Math.abs(Math.floor(((new Date()- endtime)/1000)%60,0))
      if segundos < 10
        segundos = "0"+segundos
      timerBox.innerHTML = "-" + minutos + ":" + segundos
    return

  ), 1000)
  return

setTimer = ->
  minutes = parseInt(prompt('Ingrese el n\u00FAmero de minutos', 10))
  endtime = new Date()
  endtime.setMinutes(endtime.getMinutes() + parseInt(minutes))
  startTimer(endtime.toJSON())
  ws.sendJSON
    'type': 'timer.start',
    'time': endtime.toJSON()
  return

ws.addMessageListener 'timer.start', (message) ->
  startTimer(message["time"])
      
window.addEventListener 'load', ->
  timer = document.querySelector('#timer-templates').content.querySelector("#slides-timer")
  addNodeToRemote timer, false
  timerBox = document.getElementById 'slides-timer'
  timerBox = document.getElementById('slides-timer')
  timerBox.addEventListener 'click', setTimer
  