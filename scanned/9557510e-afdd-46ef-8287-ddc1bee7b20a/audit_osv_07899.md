# [M] RTSP bad headers buffer over-read

## Summary
Severity: Medium
Advisory: CURL-CVE-2018-1000301
Aliases: CVE-2018-1000301
Published: 2018-05-16
Source: https://osv.dev/vulnerability/CURL-CVE-2018-1000301
Type: osv

## Details
curl can be tricked into reading data beyond the end of a heap based buffer
used to store downloaded content.

When servers send RTSP responses back to curl, the data starts out with a set
of headers. curl parses that data to separate it into a number of headers to
deal with those appropriately and to find the end of the headers that signal
the start of the "body" part.

The function that splits up the response into headers is called
`Curl_http_readwrite_headers()` and in situations where it cannot find a single
header in the buffer, it might end up leaving a pointer pointing into the
buffer instead of to the start of the buffer which then later on may lead to
an out of buffer read when code assumes that pointer points to a full buffer
size worth of memory to use.

This could potentially lead to information leakage but most likely a
crash/denial of service for applications if a server triggers this flaw.
