# [M] ALPINE-CVE-2017-6505

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-6505
Ecosystem: Alpine:v3.5
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6505
Type: osv

## Affected
- Alpine:v3.5: `qemu` — affected >=0 <2.8.1.1-r0

## Details
The ohci_service_ed_list function in hw/usb/hcd-ohci.c in QEMU (aka Quick Emulator) before 2.9.0 allows local guest OS users to cause a denial of service (infinite loop) via vectors involving the number of link endpoint list descriptors, a different vulnerability than CVE-2017-9330.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6505
