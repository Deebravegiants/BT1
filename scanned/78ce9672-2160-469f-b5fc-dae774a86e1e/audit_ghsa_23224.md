# [C] ThinkAdmin Administrator cookies still working after password change

## Summary
Severity: Critical
Advisory: GHSA-qv5j-rwq3-m823
CVE: CVE-2019-11018
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qv5j-rwq3-m823
Type: github-advisory

## Affected
- Packagist: `zoujingli/thinkadmin` — affected 4.0

## Details
`application\admin\controller\User.php` in ThinkAdmin V4.0 does not prevent continued use of an administrator's cookie-based credentials after a password change.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11018
- https://github.com/zoujingli/ThinkAdmin/issues/173
- https://github.com/zoujingli/ThinkAdmin
