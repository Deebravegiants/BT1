# [M] Heap overflow in libvpx

## Summary
Severity: Medium
Advisory: CVE-2023-6349
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:P/VC:L/VI:H/VA:N/SC:L/SI:H/SA:N/S:N/AU:N/R:A/V:D)
Published: 2024-05-27
Source: https://osv.dev/vulnerability/CVE-2023-6349
Type: osv

## Details
A heap overflow vulnerability exists in libvpx - Encoding a frame that has larger dimensions than the originally configured size with VP9 may result in a heap overflow in libvpx.
We recommend upgrading to version 1.13.1 or above

## References
- https://chromium.googlesource.com/
- https://chromium.googlesource.com/webm/libvpx
- https://crbug.com/webm/1642
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6349.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6349
