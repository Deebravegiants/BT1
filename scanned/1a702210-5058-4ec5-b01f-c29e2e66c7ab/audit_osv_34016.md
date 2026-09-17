# [C] OpenCV contains a use after free buffer write due to an uninitialized pointer

## Summary
Severity: Critical
Advisory: CVE-2025-53644
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-53644
Type: osv

## Details
OpenCV is an Open Source Computer Vision Library. Versions 4.10.0 and 4.11.0 have an uninitialized pointer variable on stack that may lead to arbitrary heap buffer write when reading crafted JPEG images. Version 4.12.0 fixes the vulnerability.

## References
- https://github.com/opencv/opencv/releases/tag/4.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53644.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53644
- https://securitylab.github.com/advisories/GHSL-2025-057_OpenCV/
- https://github.com/opencv/opencv/issues/27271
- https://github.com/opencv/opencv/commit/a39db41390de546d18962ee1278bd6dbb715f466
