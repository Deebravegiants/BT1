# [M] Cross-site scripting in TotalJS

## Summary
Severity: Medium
Advisory: GHSA-jj45-24rw-v6jw
CVE: CVE-2023-30094
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-04
Source: https://github.com/advisories/GHSA-jj45-24rw-v6jw
Type: github-advisory

## Affected
- npm: `total4` — affected >=0 <0.0.81

## Details
A stored cross-site scripting (XSS) vulnerability in TotalJS allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the platform name field in the settings module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30094
- https://github.com/totaljs/flow/issues/100
- https://github.com/totaljs/framework4/commit/e2cea690c3fe4453e94da896a69f832511f65179
- https://github.com/totaljs/framework4
- https://www.edoardoottavianelli.it/CVE-2023-30094
- https://www.youtube.com/watch?v=8VbTm2sIdBE
- https://www.youtube.com/watch?v=vOb9Fyg3iVo
