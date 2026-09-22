# [M] OpenFUN Richie Observable Timing Discrepancy in its sync_course_run_from_request function

## Summary
Severity: Medium
Advisory: GHSA-xjhr-fm27-4hmx
CVE: CVE-2026-26717
CWE: CWE-208
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-xjhr-fm27-4hmx
Type: github-advisory

## Affected
- PyPI: `richie` — affected >=0 <3.3.0

## Details
An issue in OpenFUN Richie (LMS) in src/richie/apps/courses/api.py. The application used the non-constant time == operator for HMAC signature verification in the sync_course_run_from_request function. This allows remote attackers to forge valid signatures and bypass authentication by measuring response time discrepancies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26717
- https://github.com/openfun/richie/commit/a1b5bbda3403d7debb466c303a32852925fcba5f
- https://github.com/Rickidevs/CVE-2026-26717
- https://github.com/openfun/richie
- https://medium.com/@ordogh/cve-2026-26717-hmac-timing-attack-in-openfun-richie-lms-f04377efe83d?postPublishedType=repub
