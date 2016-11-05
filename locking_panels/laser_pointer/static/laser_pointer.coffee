
#laser pointer


@mouseUp = ->
  window.removeEventListener 'mousemove', divMove, true 
  pointer = document.getElementById('laser_pointer')
  if pointer.style.display == "block"
    ws.sendJSON 'type': 'laser.hide'
  return

@mouseDown = (e) ->
  window.addEventListener 'mousemove', divMove, true
  return

@divMove = (e) ->
  x = e.clientX/ window.innerWidth
  y = e.clientY/ window.innerHeight
  ws.sendJSON 'type': 'laser.move', 'x':x, 'y': y
  return

@handleTouchLaserMove = (evt) ->
    x = evt.touches[0].clientX / window.innerWidth;
    y = evt.touches[0].clientY / window.innerHeight;
    ws.sendJSON 'type': 'laser.move', 'x':x, 'y': y
      
window.addEventListener 'load', ->
  pointer = document.querySelector('#laser-templates').content.querySelector("#laser_pointer")
  laserbtn = document.querySelector('#laser-templates').content.querySelector("#laser_pointer-button")
  addNodeToPresentation pointer, false
  addNodeToRemote laserbtn, false
  pointer = document.getElementById('laser_pointer-button')
  pointer.addEventListener 'mousedown', mouseDown, false
  pointer.addEventListener 'touchmove', handleTouchLaserMove
  window.addEventListener 'mouseup', mouseUp, false
  window.addEventListener 'touchend', mouseUp, false
  
#laser pointer
ws.addMessageListener 'laser.hide', (message) ->
  pointer = document.getElementById('laser_pointer')
  pointer.style.display = 'none'

ws.addMessageListener 'laser.move', (message) ->
  pointer = document.getElementById('laser_pointer')
  pointer.style.display = 'block'
  pointer.style.position = 'absolute'
  pointer.style.top = message.y * window.innerHeight + 'px'
  pointer.style.left = message.x * window.innerWidth + 'px'