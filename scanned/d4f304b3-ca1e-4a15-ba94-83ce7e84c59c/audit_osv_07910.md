# [H] TLS session caching disaster

## Summary
Severity: High
Advisory: CURL-CVE-2021-22901
Aliases: CVE-2021-22901
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CURL-CVE-2021-22901
Type: osv

## Details
libcurl can be tricked into using already freed memory when a new TLS session
is negotiated or a client certificate is requested on an existing connection.
For example, this can happen when a TLS server requests a client certificate
on a connection that was established without one. A malicious server can use
this in rare unfortunate circumstances to potentially reach remote code
execution in the client.

OpenSSL can declare a "new session" for different reasons, including the
initial TLS handshake completion, TLS 1.2 (or earlier) renegotiation, or TLS
1.3 client certificate requests. When libcurl at runtime sets up support for
session ID caching on a connection using OpenSSL, it stores pointers to the
transfer in-memory object for later retrieval when OpenSSL considers a new
session to be established.

However, if the connection is used by multiple transfers (like with a reused
HTTP/1.1 connection or multiplexed HTTP/2 connection) that first transfer
object might be freed before the new session is established on that connection
and then the function accesses a memory buffer that might be freed. When using
that memory, libcurl might even call a function pointer in the object, making
it possible for a remote code execution if the server could somehow manage to
get crafted memory content into the correct place in memory.
