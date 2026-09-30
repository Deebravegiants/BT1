# [M] CVE-2019-25043

## Summary
Severity: Medium
Advisory: CVE-2019-25043
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2019-25043
Type: osv

## Details
ModSecurity 3.x before 3.0.4 mishandles key-value pair parsing, as demonstrated by a "string index out of range" error and worker-process crash for a "Cookie: =abc" header.

## References
- https://github.com/SpiderLabs/ModSecurity/issues/2566
