# [M] ForkCMS XSS via `publish_on_date` parameter

## Summary
Severity: Medium
Advisory: GHSA-65wf-qm95-6mhm
CVE: CVE-2022-35587
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-13
Source: https://github.com/advisories/GHSA-65wf-qm95-6mhm
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <5.11.0

## Details
A cross-site scripting (XSS) issue in the Fork version 5.9.3 allows remote attackers to inject JavaScript via the `publish_on_date` Parameter. This issue was patched in version 5.11.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35587
- https://github.com/forkcms/forkcms/commit/76bf739e01f697e10c1277b9726e39b9705be296
- https://github.com/forkcms/forkcms
- https://huntr.dev/bounties/6-other-forkcms
