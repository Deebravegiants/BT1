# [M] CVE-2020-20412

## Summary
Severity: Medium
Advisory: CVE-2020-20412
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-26
Source: https://osv.dev/vulnerability/CVE-2020-20412
Type: osv

## Details
lib/codebook.c in libvorbis before 1.3.6, as used in StepMania 5.0.12 and other products, has insufficient array bounds checking via a crafted OGG file. NOTE: this may overlap CVE-2018-5146.

## References
- https://github.com/stepmania/stepmania/issues/1890
