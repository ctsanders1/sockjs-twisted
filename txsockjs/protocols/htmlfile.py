# Copyright (c) 2012, Christopher Gamble
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Christopher Gamble nor the names of its 
#      contributors may be used to endorse or promote products derived 
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

from twisted.web import http
from txsockjs.protocols.base import StubResource

class HTMLFile(StubResource):
    sent = 0
    done = False
    
    def render_GET(self, request):
        self.parent.setBaseHeaders(request)
        callback = request.args.get('c',[None])[0]
        if callback is None:
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            return '"callback" parameter required'
        request.setHeader('content-type', 'text/html; charset=UTF-8')
        request.write(r'''
<!doctype html>
<html><head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head><body><h2>Don't panic!</h2>
  <script>
    document.domain = document.domain;
    var c = parent.{};
    c.start();
    function p(d) {{c.message(d);}};
    window.onload = function() {{c.stop();}};
  </script>{}
'''.format(callback, ' '*1024))
        return self.connect(request)
    
    def write(self, data):
        if self.done:
            self.session.requeue([data])
            return
        packet = "<script>\np(\"{}\");\n</script>\r\n".format(data.replace('\\','\\\\').replace('"','\\"'))
        self.sent += len(packet)
        self.request.write(packet)
        if self.sent > self.parent._options['streaming_limit']:
            self.done = True
            self.disconnect()
    
    def writeSequence(self, data):
        for d in data:
            self.write(d)
