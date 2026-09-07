# [C] ThinkAdmin insecure unserialize vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4vp2-mj4m-69m4
CVE: CVE-2020-23653
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4vp2-mj4m-69m4
Type: github-advisory

## Affected
- Packagist: `zoujingli/thinkadmin` — affected >=4.0 <6.1.0

## Details
An insecure unserialize vulnerability was discovered in ThinkAdmin versions 4.x through 6.x in `app/admin/controller/api/Update.php `and `app/wechat/controller/api/Push.php`, which may lead to arbitrary remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23653
- https://github.com/zoujingli/ThinkAdmin/issues/238
- https://github.com/zoujingli/ThinkAdmin/commit/640a61ae0772dcd5209d74dff8ad373e61e8ad8c
- https://github.com/zoujingli/ThinkAdmin/commit/6ccd4055fc40d2d7d154920a1859a7c19774bd1a
- https://github.com/zoujingli/ThinkAdmin/commit/b8a2ded90866a285e9022c842e546d8a6fa5fa6d
- https://github.com/zoujingli/ThinkAdmin
