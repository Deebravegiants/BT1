# [M] ALPINE-CVE-2019-20485

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-20485
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.9
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20485
Type: osv

## Affected
- Alpine:v3.10: `libvirt` — affected >=0 <5.5.0-r2
- Alpine:v3.11: `libvirt` — affected >=0 <5.9.0-r2
- Alpine:v3.9: `libvirt` — affected >=0 <5.5.0-r2

## Details
qemu/qemu_driver.c in libvirt before 6.0.0 mishandles the holding of a monitor job during a query to a guest agent, which allows attackers to cause a denial of service (API blockage).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20485
