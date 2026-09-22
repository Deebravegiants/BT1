# [M] CVE-2018-19791

## Summary
Severity: Medium
Advisory: CVE-2018-19791
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-19791
Type: osv

## Details
The server in LiteSpeed OpenLiteSpeed before 1.5.0 RC6 does not correctly handle requests for byte sequences, allowing an attacker to amplify the response size by requesting the entire response body repeatedly, as demonstrated by an HTTP Range header value beginning with the "bytes=0-,0-" substring.

## References
- https://github.com/litespeedtech/openlitespeed/issues/117
