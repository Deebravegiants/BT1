# [M] python-apt Flawed Package Integrity Check

## Summary
Severity: Medium
Advisory: GHSA-rp8m-h266-53jh
CVE: CVE-2019-15795
CWE: CWE-327
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rp8m-h266-53jh
Type: github-advisory

## Affected
- PyPI: `python-apt` — affected >=0 <0.8.3ubuntu7.5
- PyPI: `python-apt` — affected >=0.9.0 <0.9.3.5ubuntu3
- PyPI: `python-apt` — affected >=1.0.0 <1.1.0
- PyPI: `python-apt` — affected >=1.2.0 <1.6.5ubuntu0.1
- PyPI: `python-apt` — affected >=1.7.0 <1.9.0ubuntu1.2

## Details
python-apt only checks the MD5 sums of downloaded files in `Version.fetch_binary()` and `Version.fetch_source()` of apt/package.py in version 1.9.0ubuntu1 and earlier. This allows a man-in-the-middle attack which could potentially be used to install altered packages and has been fixed in versions 1.9.0ubuntu1.2, 1.6.5ubuntu0.1, 1.1.0~beta1ubuntu0.16.04.7, 0.9.3.5ubuntu3+esm2, and 0.8.3ubuntu7.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15795
- https://github.com/excid3/python-apt
- https://usn.ubuntu.com/4247-1
- https://usn.ubuntu.com/4247-3
