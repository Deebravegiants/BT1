# [H] Prototype pollution in controlled-merge

## Summary
Severity: High
Advisory: GHSA-5pg7-v24c-9rp9
CVE: CVE-2020-28268
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-5pg7-v24c-9rp9
Type: github-advisory

## Affected
- npm: `controlled-merge` — affected >=1.0.0 <1.3.0

## Details
Prototype pollution vulnerability in 'controlled-merge' versions 1.0.0 through 1.2.0 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28268
- https://github.com/hlfshell/controlled-merge/commit/5a4b2e9ffe5a0be7f8843d4ab038599d3ae5f9d4
- https://www.npmjs.com/package/controlled-merge
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28268
