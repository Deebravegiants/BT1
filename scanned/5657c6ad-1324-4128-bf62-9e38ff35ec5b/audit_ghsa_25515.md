# [H] Buffer Overflow in vyper

## Summary
Severity: High
Advisory: GHSA-4mrx-6fxm-8jpg
CVE: CVE-2022-24788
CWE: CWE-119, CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2022-04-20
Source: https://github.com/advisories/GHSA-4mrx-6fxm-8jpg
Type: github-advisory

## Affected
- PyPI: `vyper` — affected >=0 <0.3.2

## Details
### Impact
Importing a function from a JSON interface which returns `bytes` generates bytecode which does not clamp bytes length, potentially resulting in a buffer overrun.

### Patches
0.3.2 (as of https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b)

### Workarounds
Use .vy interfaces.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-4mrx-6fxm-8jpg
- https://nvd.nist.gov/vuln/detail/CVE-2022-24788
- https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b
- https://github.com/pypa/advisory-database/tree/main/vulns/vyper/PYSEC-2022-197.yaml
- https://github.com/vyperlang/vyper
