# [M] ALPINE-CVE-2016-10155

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-10155
Ecosystem: Alpine:v3.5
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10155
Type: osv

## Affected
- Alpine:v3.5: `qemu` — affected >=0 <2.8.1.1-r0

## Details
Memory leak in hw/watchdog/wdt_i6300esb.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (host memory consumption and QEMU process crash) via a large number of device unplug operations.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10155
