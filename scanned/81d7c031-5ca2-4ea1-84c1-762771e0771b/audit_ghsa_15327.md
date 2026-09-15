# [H] Taipy 3.1.1 affected by CVEs on flask-core and pymongo

## Summary
Severity: High
Advisory: GHSA-pp84-v3mw-gg4w
Ecosystem: PyPI
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-pp84-v3mw-gg4w
Type: github-advisory

## Affected
- PyPI: `taipy` — affected >=0 <4.0.0

## Details
### Summary
Indirect CVEs affect Taipy 3.1.1

### Details
Taipy 3.1.1 is affected by two existing CVEs:
CVE-2024-1681 affects flask-core <4.0.1 and taipy 3.1.1 needs <=4.0.0
CVE-2024-5629 affects pymongo <4.6.3 and taipy 3.1.1 needs <=4.6.1

Please see References for further details.

### Patch
please upgrade to the following versions:

Fixed on patch versions: >=3.1.2
and on major releases: >=4.0.0

### Impact
pre-commit breaks when using dependency Taipy 3.1.1

## References
- https://github.com/Avaiga/taipy/security/advisories/GHSA-pp84-v3mw-gg4w
- https://nvd.nist.gov/vuln/detail/CVE-2024-1681
- https://nvd.nist.gov/vuln/detail/CVE-2024-5629
- https://github.com/Avaiga/taipy
- https://github.com/advisories/GHSA-84pr-m4jr-85g5
- https://github.com/advisories/GHSA-m87m-mmvp-v9qm
