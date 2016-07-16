# COPYRIGHT (c) 2016 Cristóbal Ganter
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

logout_button = document.getElementById 'logout'

#SETUP

logout_button.addEventListener 'click', logout

ws.getMessagePromise('session.start.ok').then ->
    ws.sendSafeJSON
        'type': 'getUserName'

ws.getMessagePromise('userName').then (message) ->
    document.getElementById('user-name').innerHTML = \
        message.name
