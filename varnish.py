# sd-varnish
# Packaged for Server Density by Tom Martin (https://github.com/deplorableword/sd-varnish)
# Initial Monitoring Copyright (c) 2010, Mike Zupan <mike@zcentric.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# Neither the name nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import getopt
import telnetlib
import re

class Varnish:
	def __init__(self, agentConfig, checksLogger, rawConfig):
	    self.agentConfig = agentConfig
	    self.checksLogger = checksLogger
	    self.rawConfig = rawConfig
	
	def get_value(self, pattern, fromThis):
	    result = re.search(pattern, fromThis)
	    if result is None:
	        return 0
	    return result.group(0).split()[0]
	
	def run(self):
	    stats = {}

	    host = "127.0.0.1"
	    port = 6082

	    telnet = telnetlib.Telnet()
	    telnet.open(host, port)
	    telnet.write('stats\r\n')

	    out = telnet.read_until("N duplicate purges", 10)

	    telnet.write('quit\r\n')
	    telnet.close()

	    #
	    # pulling out the hit/miss stats
	    #
	    req = self.get_value("\d+  Client requests received", out)
	    hits = self.get_value("\d+  Cache hits", out)
	    hits_pass = self.get_value("\d+  Cache hits for pass", out)
	    miss = self.get_value("\d+  Cache misses", out)
	    hit_percent = round(((float(hits) + float(hits_pass)) / (float(hits) + float(miss) + float(hits_pass))) * 100, 1)

	    stats['requests'] = req
	    stats['cache_hits'] = hits
	    stats['cache_hits_pass'] = hits_pass
	    stats['cache_miss'] = miss
	    stats['cache_percentage'] = str(hit_percent)

	    #
	    # pulling out the cache size usage
	    #
	    bytes_free = self.get_value("\d+  bytes allocated", out)
	    bytes_used = self.get_value("\d+  bytes free", out)
	    bytes_total = int(bytes_free) + int(bytes_used)

	    stats['bytes_free'] = bytes_free
	    stats['bytes_used'] = bytes_used
	    stats['bytes_total'] = str(bytes_total)


	    #
	    # pulling out the backend info
	    #
	    backend_conn = self.get_value("\d+  Backend conn. success", out)
	    backend_unhealthy = self.get_value("\d+  Backend conn. not attempted", out)
	    backend_busy = self.get_value("\d+  Backend conn. too many", out)
	    backend_fail = self.get_value("\d+  Backend conn. failures", out)
	    backend_reuse = self.get_value("\d+  Backend conn. reuses", out)
	    backend_recycle = self.get_value("\d+  Backend conn. recycles", out)
	    backend_unused = self.get_value("\d+  Backend conn. unused", out)
	    backend_req = int(backend_conn) + int(backend_unhealthy) + int(backend_busy) + int(backend_fail) + int(backend_reuse) + int(backend_recycle) + int(backend_unused) 

	    stats['backend_conn'] = backend_conn
	    stats['backend_unhealthy'] = backend_unhealthy
	    stats['backend_busy'] = backend_busy
	    stats['backend_fail'] = backend_fail
	    stats['backend_reuse'] = backend_reuse
	    stats['backend_recycle'] = backend_recycle
	    stats['backend_unused'] = backend_unused
	    stats['backend_req'] = backend_req

	    #
	    # pulling out all the thread information
	    #
	    threads_created = self.get_value("\d+  N worker threads created", out)
	    threads_running = self.get_value("\d+  N worker threads", out)
	    threads_not_created = self.get_value("\d+  N worker threads not created", out)
	    queued_requests = self.get_value("\d+  N queued work requests", out)

	    stats['threads_created'] = threads_created
	    stats['threads_running'] = threads_running
	    stats['threads_not_created'] = threads_not_created
	    stats['queued_requests'] = queued_requests

	    #
	    # getting total bytes sent to client
	    #
	    sent_header = self.get_value("\d+  Total header bytes", out)
	    sent_body = self.get_value("\d+  Total body bytes", out)
	    sent_total = int(sent_header) + int(sent_body)

	    stats['sent_header'] = sent_header
	    stats['sent_body'] = sent_body
	    stats['sent_total'] = str(sent_total)

	    return stats

