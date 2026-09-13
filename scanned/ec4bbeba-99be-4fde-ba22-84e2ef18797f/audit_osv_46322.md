# [H] TFTP Packet Buffer Overflow

## Summary
Severity: High
Advisory: CURL-CVE-2006-1061
Aliases: CVE-2006-1061
Published: 2006-03-20
Source: https://osv.dev/vulnerability/CURL-CVE-2006-1061
Type: osv

## Details
libcurl uses the given file part of a TFTP URL in a manner that allows a
malicious user to overflow a heap-based memory buffer due to the lack of
boundary check.

This overflow happens if you pass in a URL with a TFTP protocol prefix
("tftp://"), using a valid host and a path part that is longer than 512 bytes.

The affected flaw can be triggered by a redirect, if curl/libcurl is told to
follow redirects and an HTTP server points the client to a tftp URL with the
characteristics described above.
