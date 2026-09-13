# [M] pam_usb: pusb_has_virtual_input_device() silently discards EACCES, disabling remote desktop detection under non-root execution

## Summary
Severity: Medium
Advisory: CVE-2026-48792
Aliases: GHSA-pvrg-chgw-x42c
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-48792
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.9.1, src/evdev.c silently ignores EACCES errors when opening /dev/input/event* nodes, causing pusb_has_virtual_input_device() to return 0 (no virtual devices found) even when every open() call failed due to insufficient permissions. The caller in src/local.c cannot distinguish a clean absence of virtual devices from a permission-denied scan, and acts on the false negative by continuing authentication without denying. This vulnerability is fixed in 0.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48792.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-pvrg-chgw-x42c
- https://nvd.nist.gov/vuln/detail/CVE-2026-48792
- https://github.com/mcdope/pam_usb/issues/351
- https://github.com/mcdope/pam_usb/issues/55
