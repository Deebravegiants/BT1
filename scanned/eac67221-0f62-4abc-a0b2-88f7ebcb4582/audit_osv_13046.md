# [H] CVE-2018-17095

## Summary
Severity: High
Advisory: CVE-2018-17095
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-16
Source: https://osv.dev/vulnerability/CVE-2018-17095
Type: osv

## Details
An issue has been discovered in mpruett Audio File Library (aka audiofile) 0.3.6, 0.3.5, 0.3.4, 0.3.3, 0.3.2, 0.3.1, 0.3.0. A heap-based buffer overflow in Expand3To4Module::run has occurred when running sfconvert.

## References
- https://github.com/mpruett/audiofile/issues/50
- https://github.com/mpruett/audiofile/issues/51
- https://usn.ubuntu.com/3800-1/
