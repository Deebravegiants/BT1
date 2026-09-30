# [C] Asyncpg Arbitrary Code Execution Via Access to an Uninitialized Pointer

## Summary
Severity: Critical
Advisory: GHSA-2xpj-f5g2-8p7m
CVE: CVE-2020-17446
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-2xpj-f5g2-8p7m
Type: github-advisory

## Affected
- PyPI: `asyncpg` — affected >=0 <0.21.0

## Details
asyncpg before 0.21.0 allows a malicious PostgreSQL server to trigger a crash or execute arbitrary code (on a database client) via a crafted server response, because of access to an uninitialized pointer in the array data decoder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17446
- https://github.com/MagicStack/asyncpg/commit/69bcdf5bf7696b98ee708be5408fd7d854e910d0
- https://github.com/MagicStack/asyncpg
- https://github.com/MagicStack/asyncpg/releases/tag/v0.21.0
- https://github.com/advisories/GHSA-2xpj-f5g2-8p7m
- https://github.com/pypa/advisory-database/tree/main/vulns/asyncpg/PYSEC-2020-24.yaml
- https://lists.debian.org/debian-lts-announce/2020/09/msg00002.html
