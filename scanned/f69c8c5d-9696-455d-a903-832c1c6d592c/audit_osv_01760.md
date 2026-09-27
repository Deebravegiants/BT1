# [H] ALPINE-CVE-2020-14339

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14339
Ecosystem: Alpine:v3.12
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14339
Type: osv

## Affected
- Alpine:v3.12: `libvirt` — affected >=6.2.0 <6.6.0-r0

## Details
A flaw was found in libvirt, where it leaked a file descriptor for `/dev/mapper/control` into the QEMU process. This file descriptor allows for privileged operations to happen against the device-mapper on the host. This flaw allows a malicious guest user or process to perform operations outside of their standard permissions, potentially causing serious damage to the host operating system. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14339
