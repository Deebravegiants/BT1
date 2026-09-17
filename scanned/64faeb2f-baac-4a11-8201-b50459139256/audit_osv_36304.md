# [H] FreeRDP has a heap-buffer-overflow in urb_select_configuration

## Summary
Severity: High
Advisory: CVE-2026-22859
Aliases: GHSA-56f5-76qv-2r36
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22859
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.20.1, the URBDRC client does not perform bounds checking on server‑supplied MSUSB_INTERFACE_DESCRIPTOR values and uses them as indices in libusb_udev_complete_msconfig_setup, causing an out‑of‑bounds read. This vulnerability is fixed in 3.20.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.20.1
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-22859.json
- https://access.redhat.com/errata/RHSA-2026:19033
- https://access.redhat.com/errata/RHSA-2026:3067
- https://access.redhat.com/errata/RHSA-2026:3068
- https://access.redhat.com/errata/RHSA-2026:3334
- https://access.redhat.com/errata/RHSA-2026:3975
- https://access.redhat.com/errata/RHSA-2026:4121
- https://access.redhat.com/errata/RHSA-2026:4433
- https://access.redhat.com/errata/RHSA-2026:4437
- https://access.redhat.com/errata/RHSA-2026:4438
- https://access.redhat.com/errata/RHSA-2026:4439
- https://access.redhat.com/errata/RHSA-2026:4440
- https://access.redhat.com/errata/RHSA-2026:4446
- https://access.redhat.com/errata/RHSA-2026:4471
- https://access.redhat.com/errata/RHSA-2026:4489
- https://access.redhat.com/security/cve/CVE-2026-22859
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22859.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-56f5-76qv-2r36
- https://nvd.nist.gov/vuln/detail/CVE-2026-22859
