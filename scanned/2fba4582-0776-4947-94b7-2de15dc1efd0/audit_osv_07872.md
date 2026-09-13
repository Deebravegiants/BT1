# [H] TLS session resumption client cert bypass

## Summary
Severity: High
Advisory: CURL-CVE-2016-5419
Aliases: CVE-2016-5419
Published: 2016-08-03
Source: https://osv.dev/vulnerability/CURL-CVE-2016-5419
Type: osv

## Details
libcurl would attempt to resume a TLS session even if the client certificate
had changed. That is unacceptable since a server by specification is allowed
to skip the client certificate check on resume, and may instead use the old
identity which was established by the previous certificate (or no
certificate).

libcurl supports by default the use of TLS session id/ticket to resume
previous TLS sessions to speed up subsequent TLS handshakes. They are used
when for any reason an existing TLS connection could not be kept alive to make
the next handshake faster.
