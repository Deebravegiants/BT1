# [H] Command injection in pagekit

## Summary
Severity: High
Advisory: GHSA-j6mp-hx4g-p3gm
CVE: CVE-2023-41005
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-j6mp-hx4g-p3gm
Type: github-advisory

## Affected
- Packagist: `pagekit/pagekit` — affected >=0

## Details
An issue in Pagekit pagekit v.1.0.18 alows a remote attacker to execute arbitrary code via thedownloadAction and updateAction functions in UpdateController.php

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41005
- https://github.com/pagekit/pagekit/issues/977
