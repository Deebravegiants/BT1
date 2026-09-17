# [C] CVE-2020-12761

## Summary
Severity: Critical
Advisory: CVE-2020-12761
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/CVE-2020-12761
Type: osv

## Details
modules/loaders/loader_ico.c in imlib2 1.6.0 has an integer overflow (with resultant invalid memory allocations and out-of-bounds reads) via an icon with many colors in its color map.

## References
- https://git.enlightenment.org/legacy/imlib2.git/commit/?id=c95f938ff1effaf91729c050a0f1c8684da4dd63
