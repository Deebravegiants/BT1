# [H] Authentication Buffer Overflows

## Summary
Severity: High
Advisory: CURL-CVE-2005-0490
Aliases: CVE-2005-0490
Published: 2005-02-21
Source: https://osv.dev/vulnerability/CURL-CVE-2005-0490
Type: osv

## Details
Due to bad usage of the base64 decode function to a stack-based buffer without
checking the data length, it was possible for a malicious HTTP server to
overflow the client during NTLM negotiation and for an FTP server to overflow
the client during krb4 negotiation. The
[announcement](http://www.idefense.com/application/poi/display?id=202) of this
flaw was done without contacting us.
