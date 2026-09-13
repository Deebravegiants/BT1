# [C] CVE-2020-15690

## Summary
Severity: Critical
Advisory: CVE-2020-15690
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-30
Source: https://osv.dev/vulnerability/CVE-2020-15690
Type: osv

## Details
In Nim before 1.2.6, the standard library asyncftpclient lacks a check for whether a message contains a newline character.

## References
- https://github.com/nim-lang/Nim/compare/v1.2.4...v1.2.6
- http://www.openwall.com/lists/oss-security/2021/02/04/3
- https://consensys.net/diligence/vulnerabilities/nim-asyncftpd-crlf-injection/
- https://github.com/nim-lang/Nim/blob/dc5a40f3f39c6ea672e6dc6aca7f8118a69dda99/lib/pure/asyncftpclient.nim#L145
- https://github.com/tintinweb/pub/tree/master/pocs/cve-2020-15690
