# [H] ALPINE-CVE-2019-10166

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10166
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10166
Type: osv

## Affected
- Alpine:v3.10: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.11: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.12: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.7: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.8: `libvirt` — affected >=4.0.0 <5.5.0-r0
- Alpine:v3.9: `libvirt` — affected >=4.0.0 <5.5.0-r0

## Details
It was discovered that libvirtd, versions 4.x.x before 4.10.1 and 5.x.x before 5.4.1, would permit readonly clients to use the virDomainManagedSaveDefineXML() API, which would permit them to modify managed save state files. If a managed save had already been created by a privileged user, a local attacker could modify this file such that libvirtd would execute an arbitrary program when the domain was resumed.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10166
