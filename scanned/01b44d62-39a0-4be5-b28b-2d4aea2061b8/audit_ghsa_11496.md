# [M] copyparty: volflag `nohtml` did not block javascript in svg files

## Summary
Severity: Medium
Advisory: GHSA-m6hv-x64c-27mm
CVE: CVE-2026-30974
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-m6hv-x64c-27mm
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.20.11

## Details
### Summary
The `nohtml` config option, intended to prevent execution of JavaScript in user-uploaded HTML files, did not apply to SVG images.

### Details
A user with write-permission could upload an SVG containing embedded JavaScript, which would execute in the context of whichever user opens it.

This in itself is not a vulnerability; it is intended behavior according to [the SVG spec](https://www.w3.org/TR/SVG11/script.html). The vulnerability is that the `nohtml` volflag, when enabled, did not prevent this.

`nohtml`, intended for use on volumes which contains untrusted files, would correctly prevent execution of javascript in HTML files, but did not consider SVG images. This has been fixed in v1.20.11.

### Impact
The malicious JavaScript could move or delete existing files on the server, or upload new files, using the account of the person who opens the SVG.

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-m6hv-x64c-27mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-30974
- https://github.com/9001/copyparty/commit/1c9f894e149b6be3cc7de81efc93a4ce4766e0e5
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.20.11
