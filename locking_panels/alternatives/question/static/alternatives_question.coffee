# COPYRIGHT (c) 2016 Felipe Condon
#
# GNU AFFERO GENERAL PUBLIC LICENSE
#    Version 3, 19 November 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#VARIABLES
alternatives_form = document.getElementById 'alternatives_form'
get_span = null
template = null
template_content = null
template_content_input = null
template_content_label = null
template_clone = null
question_data = null
alternatives_form_name_single = null

#FUNCTIONS
@addWording = (text) ->
  alternatives_form.textContent = text

@addSimpleAlternative = (index, text) ->
  template = document.getElementById 'alternatives_template'
  template_content = template.content
  template_content_label = template.content.querySelector '.control--radio'
  get_span = template_content_label.querySelector 'span'
  template_content_input = template_content_label.querySelector 'input'
  template_content_input.value = text
  get_span.textContent = text
  template_clone = document.importNode template_content_label, true
  alternatives_form.appendChild template_clone

@addMultipleAlternative = (index, text) ->
  template = document.getElementById 'alternatives_template'
  template_content = template.content
  template_content_label = template.content.querySelector '.control--checkbox'
  get_span = template_content_label.querySelector 'span'
  template_content_input = template_content_label.querySelector 'input'
  template_content_input.value = text
  get_span.textContent = text
  template_clone = document.importNode template_content_label, true
  alternatives_form.appendChild template_clone

#SETUP
ws.addMessageListener 'alternatives.show', (message) ->
  addWording message.wording
  switchToPanel 'alternatives-question-panel'
  if message.form == 'alternatives'
    addSimpleAlternative index, text for text, index in message.answers
    @e = ->
      answers = []
      answers.push alternatives_form.alternatives_answer.value
      ws.sendJSON {'type':'alternatives.answer', \
      'id_alt':message['id_alt'],\
      'alternative':answers}
    alternatives_form.addEventListener 'change',e
    ws.addMessageListener 'alternatives.block.students', ->
      inputs = alternatives_form.querySelectorAll('input')
      a.disabled = true for a in inputs
    ws.addMessageListener 'alternatives.unblock.students', ->
      inputs = alternatives_form.querySelectorAll('input')
      a.disabled = false for a in inputs


  else if message.form == 'multiple-choices'
    addMultipleAlternative index, text for text, index in message.answers
    @e = ->
      answers = []
      i = 0
      while i < alternatives_form.length
        if alternatives_form[i].checked
          answers.push alternatives_form[i].value
        i++

      ws.sendJSON {'type':'alternatives.answer', \
      'id_alt':message['id_alt'],\
      'alternative':answers}
    alternatives_form.addEventListener 'change',e
    ws.addMessageListener 'alternatives.block.students', ->
      inputs = alternatives_form.querySelectorAll('input')
      a.disabled = true for a in inputs
    ws.addMessageListener 'alternatives.unblock.students', ->
      inputs = alternatives_form.querySelectorAll('input')
      a.disabled = false for a in inputs



ws.addMessageListener 'alternatives.close.clients', (message) ->
  alternatives_form.removeEventListener('change',e)
  switchToPanel 'user-panel'
