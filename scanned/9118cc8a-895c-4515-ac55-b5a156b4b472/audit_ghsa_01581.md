# [H] Update bitlyshortener to >=0.5.0 to prevent generating some invalid short URLs

## Summary
Severity: High
Advisory: GHSA-r82c-j4mq-5xfw
CWE: CWE-601
Ecosystem: PyPI
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-r82c-j4mq-5xfw
Type: github-advisory

## Affected
- PyPI: `bitlyshortener` — affected >=0 <0.5.0

## Details
### Impact
Due to a sudden upstream breaking change by Bitly, versions of `bitlyshortener` <0.5.0 can generate an invalid short URL when a vanity domain exists.

### Patches
Upgrading `bitlyshortener` to 0.5.0 or newer will prevent the generation of any such invalid short URLs.

### References
* [Release notes](https://github.com/impredicative/bitlyshortener/releases)

## References
- https://github.com/impredicative/bitlyshortener/security/advisories/GHSA-r82c-j4mq-5xfw
- https://github.com/impredicative/bitlyshortener/commit/3d412feb77f3daf6f71536463734c2119a55968d
- https://github.com/impredicative/bitlyshortener/releases/tag/0.5.0
- https://pypi.org/project/bitlyshortener
