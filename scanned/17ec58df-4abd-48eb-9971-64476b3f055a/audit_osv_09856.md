# [M] CVE-2017-11724

## Summary
Severity: Medium
Advisory: CVE-2017-11724
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-29
Source: https://osv.dev/vulnerability/CVE-2017-11724
Type: osv

## Details
The ReadMATImage function in coders/mat.c in ImageMagick through 6.9.9-3 and 7.x through 7.0.6-3 has memory leaks involving the quantum_info and clone_info data structures.

## References
- http://www.securityfocus.com/bid/104597
- https://github.com/ImageMagick/ImageMagick/issues/624
- https://security.gentoo.org/glsa/201711-07
