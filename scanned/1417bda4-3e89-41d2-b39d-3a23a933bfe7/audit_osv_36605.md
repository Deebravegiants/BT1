# [M] FreeRDP has a heap-buffer-overflow in urb_select_interface

## Summary
Severity: Medium
Advisory: CVE-2026-24679
Aliases: GHSA-2jp4-67x6-gv7x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24679
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, The URBDRC client uses server-supplied interface numbers as array indices without bounds checks, causing an out-of-bounds read in libusb_udev_select_interface. This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24679.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-2jp4-67x6-gv7x
- https://nvd.nist.gov/vuln/detail/CVE-2026-24679
- https://github.com/FreeRDP/FreeRDP/commit/2d563a50be17c1b407ca448b1321378c0726dd31
