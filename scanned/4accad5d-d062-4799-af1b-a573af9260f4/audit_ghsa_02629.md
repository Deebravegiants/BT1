# [C] Prototype Pollution in deephas

## Summary
Severity: Critical
Advisory: GHSA-4fr2-j4g9-mppf
CVE: CVE-2020-28271
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-24
Source: https://github.com/advisories/GHSA-4fr2-j4g9-mppf
Type: github-advisory

## Affected
- npm: `deephas` — affected >=1.0.0

## Details
Prototype pollution vulnerability in 'deephas' versions 1.0.0 through 1.0.5 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28271
- https://github.com/sharpred/deepHas/commit/2fe011713a6178c50f7deb6f039a8e5435981e20
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28271
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28271,
