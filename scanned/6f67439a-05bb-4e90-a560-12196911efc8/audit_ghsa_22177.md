# [M] GeniXCMS Mailbox validation logic vulnerability

## Summary
Severity: Medium
Advisory: GHSA-559c-w54x-8342
CVE: CVE-2017-8388
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-559c-w54x-8342
Type: github-advisory

## Affected
- Packagist: `genix/cms` — affected >=0 <1.1.0

## Details
GeniXCMS 1.0.2 allows remote attackers to bypass the alertDanger MSG_USER_EMAIL_EXIST protection mechanism via a register.php?act=edit&id=1 request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8388
- https://github.com/semplon/GeniXCMS/issues/72
- https://github.com/semplon/GeniXCMS/commit/e0ad60b2bb967fa3f63c35b92afe84c5f3b31009
- https://github.com/GeniXCMS/GeniXCMS
