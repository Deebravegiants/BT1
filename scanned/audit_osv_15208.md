# [H] CVE-2019-14491

## Summary
Severity: High
Advisory: CVE-2019-14491
Aliases: GHSA-fm39-cw8h-3p63, PYSEC-2026-2797, PYSEC-2026-2818, PYSEC-2026-2836, PYSEC-2026-720
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2019-08-01
Source: https://osv.dev/vulnerability/CVE-2019-14491
Type: osv

## Details
An issue was discovered in OpenCV before 3.4.7 and 4.x before 4.1.1. There is an out of bounds read in the function cv::predictOrdered<cv::HaarEvaluator> in modules/objdetect/src/cascadedetect.hpp, which leads to denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HPFLN6QAX6SUA4XR4NMKKXX26H3TYCVQ/
- https://github.com/opencv/opencv/compare/33b765d...4a7ca5a
- https://github.com/opencv/opencv/compare/371bba8...ddbd10c
- https://github.com/opencv/opencv/issues/15125
