# [H] FITS GZIP decompression bomb in Pillow

## Summary
Severity: High
Advisory: GHSA-whj4-6x5x-4v2j
CVE: CVE-2026-40192
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-whj4-6x5x-4v2j
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=10.3.0 <12.2.0

## Details
### Impact
Pillow did not limit the amount of GZIP-compressed data read when decoding a FITS image, making it vulnerable to decompression bomb attacks. A specially crafted FITS file could cause unbounded memory consumption, leading to denial of service (OOM crash or severe performance degradation).

### Patches
The amount of data read is now limited to the necessary amount.
Fixed in Pillow 12.2.0 (PR #9521).

### Workarounds
Avoid Pillow >= 10.3.0, < 12.2.0
Only open [specific image formats](https://pillow.readthedocs.io/en/stable/releasenotes/8.0.0.html#image-open-add-formats-parameter), excluding FITS.

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-whj4-6x5x-4v2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-40192
- https://github.com/python-pillow/Pillow/pull/9521
- https://github.com/python-pillow/Pillow/commit/3cb854e8b2bab43f40e342e665f9340d861aa628
- https://github.com/python-pillow/Pillow
- https://pillow.readthedocs.io/en/stable/releasenotes/12.2.0.html#prevent-fits-decompression-bomb
