# [M] Invalid URL generation in bitlyshortener

## Summary
Severity: Medium
Advisory: GHSA-rcrv-228c-gprj
Ecosystem: PyPI
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-rcrv-228c-gprj
Type: github-advisory

## Affected
- PyPI: `bitlyshortener` — affected >=0 <0.6.0

## Details
### Impact
Due to a sudden upstream breaking change by Bitly, versions of `bitlyshortener` <0.6.0 generate invalid short URLs. All users are affected and must update immediately.

### Patches
Upgrading `bitlyshortener` to 0.6.0 or newer will prevent the generation such invalid short URLs.

### Workarounds
A workaround is to replace "https://j.mp/" in each generated short URL with "https://bit.ly/".

### References
* [Release notes](https://github.com/impredicative/bitlyshortener/releases)

## References
- https://github.com/impredicative/bitlyshortener/security/advisories/GHSA-rcrv-228c-gprj
- https://github.com/impredicative/bitlyshortener/commit/b307d70bedf745305fa0dd3c5c600d8cb88d09b5
- https://github.com/impredicative/bitlyshortener
- https://github.com/impredicative/bitlyshortener/releases/tag/0.6.0
