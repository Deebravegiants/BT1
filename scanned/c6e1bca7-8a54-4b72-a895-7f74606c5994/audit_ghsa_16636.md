# [M] Moodle Logout CSRF in admin/tool/mfa/auth.php

## Summary
Severity: Medium
Advisory: GHSA-8g5h-gjwq-w5ch
CVE: CVE-2024-34007
CWE: CWE-352
Ecosystem: Packagist
Published: 2024-05-31
Source: https://github.com/advisories/GHSA-8g5h-gjwq-w5ch
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.4

## Details
The logout option within MFA did not include the necessary token to avoid the risk of users inadvertently being logged out via CSRF.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34007
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=458396
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-80877
