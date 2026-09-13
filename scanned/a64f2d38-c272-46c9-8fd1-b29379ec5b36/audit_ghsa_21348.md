# [M] kamadak-exif vulnerable to Infinite loop when parsing PNG files

## Summary
Severity: Medium
Advisory: GHSA-px9g-8hgv-jvg2
CVE: CVE-2021-21235
CWE: CWE-400, CWE-835
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-px9g-8hgv-jvg2
Type: github-advisory

## Affected
- crates.io: `kamadak-exif` — affected >=0.5.2 <0.5.3

## Details
### Impact
Reader::read_from_container can cause an infinite loop when a crafted PNG file is given.

### Patches
Version 0.5.3 includes the fix.

### Workarounds
No workaround is available.
Applications that do not pass files with the PNG signature to Reader::read_from_container are not affected.

### References
* <https://github.com/kamadak/exif-rs/security/advisories/GHSA-px9g-8hgv-jvg2>
* <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-21235>

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github.com/kamadak/exif-rs](https://github.com/kamadak/exif-rs)

## References
- https://github.com/kamadak/exif-rs/security/advisories/GHSA-px9g-8hgv-jvg2
- https://nvd.nist.gov/vuln/detail/CVE-2021-21235
- https://github.com/kamadak/exif-rs/commit/1b05eab57e484cd7d576d4357b9cda7fdc57df8c
- https://github.com/kamadak/exif-rs/commit/f21df24616ea611c5d5d0e0e2f8042eb74d5ff48
- https://crates.io/crates/kamadak-exif
- https://github.com/kamadak/exif-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0143.html
