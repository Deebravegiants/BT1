# [M] Copyparty vulnerable to file/dirkey confusion

## Summary
Severity: Medium
Advisory: GHSA-x5pq-m9p8-f4vx
CVE: CVE-2026-70657
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-x5pq-m9p8-f4vx
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.20.17

## Details
A valid filekey could potentially be converted into a dirkey, granting read-access to the containing folder.

This issue only affected volumes which simultaneously enable both filekeys and dirkeys, with volflag `dk` or `dks` combined with `fk` or `fka`.

Both required features are default-disabled, and must be explicitly enabled in the volflags (the "flags" section of a volume).

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-x5pq-m9p8-f4vx
- https://github.com/9001/copyparty/commit/e40755331ba9449993ff482456e6bdd2c6deb950
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.20.17
