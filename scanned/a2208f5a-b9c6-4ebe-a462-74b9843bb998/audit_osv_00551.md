# [M] ALPINE-CVE-2017-15596

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-15596
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 6.0 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15596
Type: osv

## Affected
- Alpine:v3.4: `xen` — affected >=0 <4.6.6-r2
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r3
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r0

## Details
An issue was discovered in Xen 4.4.x through 4.9.x allowing ARM guest OS users to cause a denial of service (prevent physical CPU usage) because of lock mishandling upon detection of an add-to-physmap error.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15596
