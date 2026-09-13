# [M] Exposure of Sensitive Information to an Unauthorized Actor in nanoid

## Summary
Severity: Medium
Advisory: GHSA-qrpm-p2h7-hrv2
CVE: CVE-2021-23566
CWE: CWE-200, CWE-704
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-qrpm-p2h7-hrv2
Type: github-advisory

## Affected
- npm: `nanoid` — affected >=3.0.0 <3.1.31

## Details
The package nanoid from 3.0.0, before 3.1.31, are vulnerable to Information Exposure via the valueOf() function which allows to reproduce the last id generated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23566
- https://github.com/ai/nanoid/pull/328
- https://github.com/ai/nanoid/commit/2b7bd9332bc49b6330c7ddb08e5c661833db2575
- https://gist.github.com/artalar/bc6d1eb9a3477d15d2772e876169a444
- https://github.com/ai/nanoid
- https://lists.debian.org/debian-lts-announce/2024/12/msg00025.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00006.html
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2332550
- https://snyk.io/vuln/SNYK-JS-NANOID-2332193
