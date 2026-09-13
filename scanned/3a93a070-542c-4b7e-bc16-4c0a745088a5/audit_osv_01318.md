# [H] ALPINE-CVE-2019-10161

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10161
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10161
Type: osv

## Affected
- Alpine:v3.10: `libvirt` — affected >=5.0.0 <5.5.0-r0
- Alpine:v3.11: `libvirt` — affected >=5.0.0 <5.5.0-r0
- Alpine:v3.12: `libvirt` — affected >=5.0.0 <5.5.0-r0
- Alpine:v3.7: `libvirt` — affected >=5.0.0 <5.5.0-r0
- Alpine:v3.8: `libvirt` — affected >=5.0.0 <5.5.0-r0
- Alpine:v3.9: `libvirt` — affected >=5.0.0 <5.5.0-r0

## Details
It was discovered that libvirtd before versions 4.10.1 and 5.4.1 would permit read-only clients to use the virDomainSaveImageGetXMLDesc() API, specifying an arbitrary path which would be accessed with the permissions of the libvirtd process. An attacker with access to the libvirtd socket could use this to probe the existence of arbitrary files, cause denial of service or cause libvirtd to execute arbitrary programs.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10161
