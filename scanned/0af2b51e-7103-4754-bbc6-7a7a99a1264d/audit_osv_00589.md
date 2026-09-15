# [M] ALPINE-CVE-2017-17565

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-17565
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-12-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17565
Type: osv

## Affected
- Alpine:v3.4: `xen` — affected >=0 <4.6.6-r3
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r5
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r5

## Details
An issue was discovered in Xen through 4.9.x allowing PV guest OS users to cause a denial of service (host OS crash) if shadow mode and log-dirty mode are in place, because of an incorrect assertion related to M2P.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17565
