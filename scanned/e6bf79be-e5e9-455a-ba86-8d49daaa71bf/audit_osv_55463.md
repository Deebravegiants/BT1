# [C] DjVuLibre OOB-Write Vulnerability in MMRDecoder

## Summary
Severity: Critical
Advisory: CVE-2025-53367
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-53367
Type: osv

## Details
DjVuLibre is a GPL implementation of DjVu, a web-centric format for distributing documents and images. Prior to version 3.5.29, the MMRDecoder::scanruns method is affected by an OOB-write vulnerability, because it does not check that the xr pointer stays within the bounds of the allocated buffer. This can lead to writes beyond the allocated memory, resulting in a heap corruption condition. An out-of-bounds read with pr is also possible for the same reason. This issue has been patched in version 3.5.29.

## References
- https://securitylab.github.com/advisories/GHSL-2025-055_DjVuLibre/
- https://github.blog/security/vulnerability-research/cve-2025-53367-an-exploitable-out-of-bounds-write-in-djvulibre
- https://github.blog/security/vulnerability-research/cve-2025-53367-an-exploitable-out-of-bounds-write-in-djvulibre/
- https://github.com/github/securitylab/tree/main/SecurityExploits/DjVuLibre/MMRDecoder_scanruns_CVE-2025-53367
- https://sourceforge.net/p/djvu/djvulibre-git/ci/33f645196593d70bd5e37f55b63886c31c82c3da
- https://www.openwall.com/lists/oss-security/2025/07/03/1
