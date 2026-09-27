# [M] Win CE Schannel cert name out of buffer read

## Summary
Severity: Medium
Advisory: CURL-CVE-2016-9953
Aliases: CVE-2016-9953
Published: 2016-12-21
Source: https://osv.dev/vulnerability/CURL-CVE-2016-9953
Type: osv

## Details
curl's TLS server certificate checks are flawed on Windows CE.

This vulnerability occurs in the verify certificate function when comparing a
wildcard certificate name (as returned by the Windows API function
`CertGetNameString()` to the hostname used to make the connection to the
server.

The pattern matching logic exhibits an out of bounds read. If the wildcard
certificate name field is longer than the connection hostname, the wildcard
comparison code performs an access out of bounds of the connection hostname
heap based buffer. This issue could technically leak the contents of memory
immediately preceding the connection hostname buffer, a crash or at worst
happen to match against another piece of data.
