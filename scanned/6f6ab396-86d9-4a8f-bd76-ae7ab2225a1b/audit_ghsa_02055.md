# [H] Denial of service in css-what

## Summary
Severity: High
Advisory: GHSA-q8pj-2vqx-8ggc
CVE: CVE-2021-33587
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-07
Source: https://github.com/advisories/GHSA-q8pj-2vqx-8ggc
Type: github-advisory

## Affected
- npm: `css-what` — affected >=4.0.0 <5.0.1

## Details
The css-what package 4.0.0 through 5.0.0 for Node.js does not ensure that attribute parsing has Linear Time Complexity relative to the size of the input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33587
- https://github.com/fb55/css-what/commit/4cdaacfd0d4b6fd00614be030da0dea6c2994655
- https://github.com/fb55/css-what
- https://github.com/fb55/css-what/releases/tag/v5.0.1
- https://lists.debian.org/debian-lts-announce/2023/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20210706-0007
