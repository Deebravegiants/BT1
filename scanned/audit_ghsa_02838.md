# [C] Prototype pollution vulnerability in 'deepref'

## Summary
Severity: Critical
Advisory: GHSA-7c7g-72q7-4xhm
CVE: CVE-2020-28274
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-7c7g-72q7-4xhm
Type: github-advisory

## Affected
- npm: `deepref` — affected >=1.1.1

## Details
Prototype pollution vulnerability in 'deepref' versions 1.1.1 through 1.2.1 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28274
- https://github.com/isaymatato/deepref
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28274,https://github.com/isaymatato/deepref/commit/24935e6a1060cb09c641d3075982f0b44cfca4c2
