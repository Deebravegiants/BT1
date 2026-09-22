# [M] RTSP RTP buffer over-read

## Summary
Severity: Medium
Advisory: CURL-CVE-2018-1000122
Aliases: CVE-2018-1000122
Published: 2018-03-14
Source: https://osv.dev/vulnerability/CURL-CVE-2018-1000122
Type: osv

## Details
curl can be tricked into copying data beyond end of its heap based buffer.

When asked to transfer an RTSP URL, curl could calculate a wrong data length
to copy from the read buffer. The `memcpy()` call would copy data from the
heap following the buffer to a storage area that would subsequently be
delivered to the application (if it did not cause a crash). We have managed to
get it to reach several hundreds bytes out of range.

This could lead to information leakage or a denial of service for the
application if the server offering the RTSP data can trigger this.
