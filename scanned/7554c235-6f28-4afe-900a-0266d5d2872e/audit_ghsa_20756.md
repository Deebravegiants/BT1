# [M] ForkCMS XSS via `publish_on_time` parameter

## Summary
Severity: Medium
Advisory: GHSA-q4qv-3x58-rxmh
CVE: CVE-2022-35589
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-13
Source: https://github.com/advisories/GHSA-q4qv-3x58-rxmh
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <5.11.0

## Details
A cross-site scripting (XSS) issue in the Fork version 5.9.3 allows remote attackers to inject JavaScript via the `publish_on_time` Parameter. This issue was patched in version 5.11.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35589
- https://github.com/forkcms/forkcms/commit/76bf739e01f697e10c1277b9726e39b9705be296
- https://github.com/forkcms/forkcms
- https://huntr.dev/bounties/7-other-forkcms
