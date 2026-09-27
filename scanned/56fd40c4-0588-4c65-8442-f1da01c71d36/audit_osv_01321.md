# [H] ALPINE-CVE-2019-10167

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10167
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10167
Type: osv

## Affected
- Alpine:v3.10: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.11: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.12: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.7: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.8: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.9: `libvirt` — affected >=4.0.0 <5.5.0-r0

## Details
The virConnectGetDomainCapabilities() libvirt API, versions 4.x.x before 4.10.1 and 5.x.x before 5.4.1, accepts an "emulatorbin" argument to specify the program providing emulation for a domain. Since v1.2.19, libvirt will execute that program to probe the domain's capabilities. Read-only clients could specify an arbitrary path for this argument, causing libvirtd to execute a crafted executable with its own privileges.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10167
