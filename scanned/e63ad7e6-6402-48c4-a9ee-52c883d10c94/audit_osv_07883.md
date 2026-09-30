# [M] Win CE Schannel cert wildcard matches too much

## Summary
Severity: Medium
Advisory: CURL-CVE-2016-9952
Aliases: CVE-2016-9952
Published: 2016-12-21
Source: https://osv.dev/vulnerability/CURL-CVE-2016-9952
Type: osv

## Details
curl's TLS server certificate checks are flawed on Windows CE.

This vulnerability occurs in the verify certificate function when comparing a
wildcard certificate name (as returned by the Windows API function
`CertGetNameString)` to the hostname used to make the connection to the
server.

The vulnerability can be triggered with an overly permissive wildcard SAN in
the server certificate such as a DNS name of `*.com`. When the function
compares the cert name to the connection hostname, the wildcard character is
removed from the cert name and the connection hostname is checked to see if it
ends with the modified cert name. This means a hostname of example.com would
match a DNS SAN of `*.com`, among other variations. This approach violates
recommendations in RFC 6125 and could lead to MITM attacks.
