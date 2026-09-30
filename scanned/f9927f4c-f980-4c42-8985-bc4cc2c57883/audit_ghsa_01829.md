# [C] Prototype polluation in just-safe-set

## Summary
Severity: Critical
Advisory: GHSA-v26w-gcxh-v4r7
CVE: CVE-2021-25952
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-v26w-gcxh-v4r7
Type: github-advisory

## Affected
- npm: `just-safe-set` — affected >=1.0.0 <2.2.2

## Details
Prototype pollution vulnerability in ‘just-safe-set’ versions 1.0.0 through 2.2.1 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25952
- https://github.com/angus-c/just/pull/267
- https://github.com/angus-c/just/commit/dd57a476f4bb9d78c6f60741898dc04c71d2eb53
- https://github.com/angus-c/just
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25952
