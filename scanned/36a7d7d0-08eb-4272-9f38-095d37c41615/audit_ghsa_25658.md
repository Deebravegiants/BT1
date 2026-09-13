# [H] MantisBT CSV Injection unprivileged user access in csv_export.php

## Summary
Severity: High
Advisory: GHSA-rg8f-5p7x-m6wv
CVE: CVE-2021-43257
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-15
Source: https://github.com/advisories/GHSA-rg8f-5p7x-m6wv
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.25.3

## Details
Lack of Neutralization of Formula Elements in the CSV API of MantisBT before 2.25.3 allows an unprivileged attacker to execute code or gain access to information when a user opens the csv_export.php generated CSV file in Excel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43257
- https://github.com/mantisbt/mantisbt/commit/7f4534c723e3162b8784aebda4836324041dbc3e
- https://github.com/mantisbt/mantisbt/commit/99eb8d41cbacc703f88807898dcc9ac55eec0f15
- https://github.com/mantisbt/mantisbt
- https://www.mantisbt.org/bugs/view.php?id=29130
