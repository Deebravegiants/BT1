# [M] ALPINE-CVE-2020-12430

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-12430
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-12430
Type: osv

## Affected
- Alpine:v3.10: `libvirt` — affected >=4.10.0 <5.5.0-r1
- Alpine:v3.11: `libvirt` — affected >=4.10.0 <5.9.0-r1
- Alpine:v3.8: `libvirt` — affected >=4.10.0 <5.5.0-r1
- Alpine:v3.9: `libvirt` — affected >=4.10.0 <5.5.0-r1

## Details
An issue was discovered in qemuDomainGetStatsIOThread in qemu/qemu_driver.c in libvirt 4.10.0 though 6.x before 6.1.0. A memory leak was found in the virDomainListGetStats libvirt API that is responsible for retrieving domain statistics when managing QEMU guests. This flaw allows unprivileged users with a read-only connection to cause a memory leak in the domstats command, resulting in a potential denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-12430
