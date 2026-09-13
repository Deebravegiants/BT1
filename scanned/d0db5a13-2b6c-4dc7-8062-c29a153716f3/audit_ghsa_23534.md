# [H] Buffer over-flow in Pillow

## Summary
Severity: High
Advisory: GHSA-hr8g-f6r6-mr22
CVE: CVE-2022-30595
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-26
Source: https://github.com/advisories/GHSA-hr8g-f6r6-mr22
Type: github-advisory

## Affected
- PyPI: `Pillow` — affected >=9.1.0 <9.1.1

## Details
When reading a TGA file with RLE packets that cross scan lines, Pillow reads the information past the end of the first line without deducting that from the length of the remaining file data. This vulnerability was introduced in Pillow 9.1.0, and can cause a heap buffer overflow.

Opening an image with a zero or negative height has been found to bypass a decompression bomb check. This will now raise a SyntaxError instead, in turn raising a PIL.UnidentifiedImageError.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30595
- https://github.com/python-pillow/Pillow/commit/c846cc881ebe34e3518412c2e3636433d9947280
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2022-43145.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/main/src/libImaging/TgaRleDecode.c
- https://pillow.readthedocs.io/en/stable/releasenotes/9.1.1.html
