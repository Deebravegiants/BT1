# [H] CVE-2019-14492

## Summary
Severity: High
Advisory: CVE-2019-14492
Aliases: GHSA-fw99-f933-rgh8, PYSEC-2026-2798, PYSEC-2026-2821, PYSEC-2026-2837, PYSEC-2026-721
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-01
Source: https://osv.dev/vulnerability/CVE-2019-14492
Type: osv

## Details
An issue was discovered in OpenCV before 3.4.7 and 4.x before 4.1.1. There is an out of bounds read/write in the function HaarEvaluator::OptFeature::calc in modules/objdetect/src/cascadedetect.hpp, which leads to denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00025.html
- https://github.com/opencv/opencv/compare/33b765d...4a7ca5a
- https://github.com/opencv/opencv/compare/371bba8...ddbd10c
- https://github.com/opencv/opencv/issues/15124
