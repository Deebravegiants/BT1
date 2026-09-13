# [H] BIT-weblate-2022-23915

## Summary
Severity: High
Advisory: BIT-weblate-2022-23915
Aliases: CVE-2022-23915, CVE-2022-24727, GHSA-3872-f48p-pxqj, GHSA-h2g5-2rhx-ffgj, PYSEC-2022-162, PYSEC-2022-31, SNYK-PYTHON-WEBLATE-2414088
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-weblate-2022-23915
Type: osv

## Affected
- Bitnami: `weblate` — affected >=0 <4.11.1

## Details
The package weblate from 0 and before 4.11.1 are vulnerable to Remote Code Execution (RCE) via argument injection when using git or mercurial repositories. Authenticated users, can change the behavior of the application in an unintended way, leading to command execution.

## References
- https://github.com/WeblateOrg/weblate/pull/7337
- https://github.com/WeblateOrg/weblate/pull/7338
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-4.11.1
- https://snyk.io/vuln/SNYK-PYTHON-WEBLATE-2414088
