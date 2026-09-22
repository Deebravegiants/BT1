# [M] FreeRDP has a Heap-use-after-free in urb_select_interface

## Summary
Severity: Medium
Advisory: CVE-2026-24675
Aliases: GHSA-x9jr-99h2-g7mj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24675
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, urb_select_interface can free the device's MS config on error but later code still dereferences it, leading to a use after free in libusb_udev_select_interface. This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24675.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-x9jr-99h2-g7mj
- https://nvd.nist.gov/vuln/detail/CVE-2026-24675
- https://github.com/FreeRDP/FreeRDP/commit/d676518809c319eec15911c705c13536036af2ae
