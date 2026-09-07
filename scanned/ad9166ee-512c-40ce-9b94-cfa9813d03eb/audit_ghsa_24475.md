# [H] OpenEXR invalid write

## Summary
Severity: High
Advisory: GHSA-qxh9-r8xw-7v99
CVE: CVE-2017-9111
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qxh9-r8xw-7v99
Type: github-advisory

## Affected
- PyPI: `OpenEXR` — affected >=0 <2.2.1

## Details
In OpenEXR 2.2.0, an invalid write of size 8 in the storeSSE function in ImfOptimizedPixelReading.h could cause the application to crash or execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9111
- https://github.com/openexr/openexr/issues/232
- https://github.com/openexr/openexr/pull/233
- https://github.com/AcademySoftwareFoundation/openexr
- https://github.com/openexr/openexr/releases/tag/v2.2.1
- https://lists.debian.org/debian-lts-announce/2020/08/msg00056.html
- https://usn.ubuntu.com/4148-1
- https://usn.ubuntu.com/4339-1
- https://www.debian.org/security/2020/dsa-4755
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00000.html
- http://www.openwall.com/lists/oss-security/2017/05/12/5
