loadError = ->
  showErrorBubble(
    'Ha ocurrido un error al intentar subir el archivo!'
  )
  
image_input_funct = ->
  image_input = document.getElementById 'slides-add-pic'
  image_input.addEventListener 'change', ->
    pg = document.getElementById 'upload-pic-prog'
    file = image_input.files[0]
    up1 = '<svg fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
          </svg>'
    up2 = '<svg fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                <path d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
            </svg>'
    fr = new FileReader()
    fr.onprogress = (progress) ->
      pg.innerHTML = (progress.loaded / progress.total)*100 + "%"
      
    fr.onload = ->
      buffer = new Uint8Array(fr.result)
      pg.innerHTML = up1 + up2
      ws.sendJSONIfOpen(
        {
          'type': 'pic.upload'
          'mime': file.type
          'data': Unibabel.bufferToBase64(buffer)
          'name': file.name
        }
      )
  
    fr.onerror = loadError
    fr.readAsArrayBuffer file
  
ws.addMessageListener 'pic.upload.ok', (message) ->
  pg = document.getElementById 'upload-pic-prog'
  loaded = '<svg fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 7l-1.41-1.41-6.34 6.34 1.41 1.41L18 7zm4.24-1.41L11.66 16.17 7.48 12l-1.41 1.41L11.66 19l12-12-1.42-1.41zM.41 13.41L6 19l1.41-1.41L1.83 12 .41 13.41z"/>
        </svg>'
  pg.innerHTML = loaded
  addSlide message.newSlide
  
      
window.addEventListener 'load', ->
  pic_add = document.querySelector('#picture-upload-templates')
  input = pic_add.content.querySelector("input")
  button = pic_add.content.querySelector("#add-pic-label")
  addNodeToRemote input, false
  addNodeToRemote button, false
  image_input_funct()

  