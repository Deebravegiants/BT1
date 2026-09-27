# [C] CVE-2018-16836

## Summary
Severity: Critical
Advisory: CVE-2018-16836
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-11
Source: https://osv.dev/vulnerability/CVE-2018-16836
Type: osv

## Details
Rubedo through 3.4.0 contains a Directory Traversal vulnerability in the theme component, allowing unauthenticated attackers to read and execute arbitrary files outside of the service root path, as demonstrated by a /theme/default/img/%2e%2e/..//etc/passwd URI.

## References
- https://github.com/maroueneboubakri/CVE/tree/master/rubedo-cms
- https://www.exploit-db.com/exploits/45385/
