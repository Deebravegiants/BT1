# [M] mod_http2, read-after-free in h2 connection shutdown (CVE-2019-10082)

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Use After Free
Reporter: cy1337
State: resolved
Disclosed: 2019-10-15T18:00:52.377Z
CVE: CVE-2019-10082
Source: https://hackerone.com/reports/680415

## Details
Using fuzzed network input, the http/2 session handling could be made to read memory after being freed, during connection shutdown. This is made possible by a race condition in which nghttp2 maintains a reference to a stream after mod_http2 has destroyed it.

This vulnerability has been fixed in 2.4.41 and affects versions as far back as 2.4.18.

Using [http2fuzz](https://github.com/c0nrad/http2fuzz) against an ASAN build of httpd with `MaxMemFree 1` will quickly reproduce crashes like this:
```
=================================================================
==22097==ERROR: AddressSanitizer: heap-use-after-free on address 0x6250042609b8 at pc 0x0000008d63f3 bp 0x7fd8c39f9420 sp 0x7fd8c39f9410
READ of size 4 at 0x6250042609b8 thread T1044
    #0 0x8d63f2 in h2_stream_send_frame /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_stream.c:377
    #1 0x8b04be in on_frame_send_cb /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_session.c:593
    #2 0x7fdade4b14c4 in session_call_on_frame_send /home/cyoung/http2_fuzz/nghttp2-1.36.0/lib/nghttp2_session.c:2396
    #3 0x7fdade4b20bf in session_after_frame_sent1 /home/cyoung/http2_fuzz/nghttp2-1.36.0/lib/nghttp2_session.c:2593
    #4 0x7fdade4b3b0b in nghttp2_session_mem_send_internal /home/cyoung/http2_fuzz/nghttp2-1.36.0/lib/nghttp2_session.c:3088
    #5 0x7fdade4b4232 in nghttp2_session_send /home/cyoung/http2_fuzz/nghttp2-1.36.0/lib/nghttp2_session.c:3239
    #6 0x8bca05 in h2_session_send /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_session.c:1318
    #7 0x8ce194 in h2_session_process /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_session.c:2269
    #8 0x873b76 in h2_conn_run /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_conn.c:208
    #9 0x883731 in h2_h2_process_conn /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_h2.c:657
    #10 0x4f4c90 in ap_run_process_connection /home/cyoung/http2_fuzz/httpd-2.4.39/server/connection.c:42
    #11 0x9d7e74 in process_socket /home/cyoung/http2_fuzz/httpd-2.4.39/server/mpm/event/event.c:1050
    #12 0x9de78f in worker_thread /home/cyoung/http2_fuzz/httpd-2.4.39/server/mpm/event/event.c:2083
    #13 0x7fdadd58b92d in dummy_worker threadproc/unix/thread.c:142
    #14 0x7fdadd0c36b9 in start_thread (/lib/x86_64-linux-gnu/libpthread.so.0+0x76b9)
    #15 0x7fdadcdf941c in clone (/lib/x86_64-linux-gnu/libc.so.6+0x10741c)

0x6250042609b8 is located 184 bytes inside of 8192-byte region [0x625004260900,0x625004262900)
freed by thread T1044 here:
    #0 0x7fdadee3d2ca in __interceptor_free (/usr/lib/x86_64-linux-gnu/libasan.so.2+0x982ca)
    #1 0x7fdadd55cf3e in allocator_free memory/unix/apr_pools.c:507
    #2 0x7fdadd55e19c in apr_pool_destroy memory/unix/apr_pools.c:1043
    #3 0x8dc458 in h2_stream_destroy /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_stream.c:584
    #4 0x88926d in stream_destroy_iter /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_mplx.c:320
    #5 0x8f92ac in ihash_iter /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_util.c:275
    #6 0x7fdadd53c246 in apr_hash_do tables/apr_hash.c:542
    #7 0x8f939d in h2_ihash_iter /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_util.c:283
    #8 0x88933f in purge_streams /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_mplx.c:328
    #9 0x899ac4 in h2_mplx_dispatch_master_events /home/cyoung/http2_fuzz/httpd-2.4.39/modules/http2/h2_mplx.c:1066
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/680415_
