xDown = null
yDown = null

handleTouchStart = (evt) ->
  xDown = evt.touches[0].clientX
  yDown = evt.touches[0].clientY


handleTouchMove = (evt) ->
  if active_panel == "presentation-panel" || active_panel == "remote-panel"
    xUp = evt.touches[0].clientX;
    yUp = evt.touches[0].clientY;
    xDiff = xDown - xUp;
    yDiff = yDown - yUp;
    if xDiff > 150
      xDown = xUp
      ws.sendJSON 'type': 'slides.next'
    else if xDiff < -150
      xDown = xUp
      ws.sendJSON 'type': 'slides.prev'



window.addEventListener 'load', ->
  slider_zone = document.querySelector('#slider-zone-templates').content.querySelector("#slides-slider-zone")
  addNodeToRemote slider_zone, false
  slider_zone = document.querySelector('#slides-slider-zone')
  slider_zone.addEventListener 'touchstart', handleTouchStart
  slider_zone.addEventListener 'touchmove', handleTouchMove
  
  