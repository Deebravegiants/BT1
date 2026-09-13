# [H] ALPINE-CVE-2017-1000256

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-1000256
Ecosystem: Alpine:v3.5, Alpine:v3.6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000256
Type: osv

## Affected
- Alpine:v3.5: `libvirt` — affected >=2.3.0 <2.5.0-r2
- Alpine:v3.6: `libvirt` — affected >=2.3.0 <3.3.0-r2

## Details
libvirt version 2.3.0 and later is vulnerable to a bad default configuration of "verify-peer=no" passed to QEMU by libvirt resulting in a failure to validate SSL/TLS certificates by default.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000256
