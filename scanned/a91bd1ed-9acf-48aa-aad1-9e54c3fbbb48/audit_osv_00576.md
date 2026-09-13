# [M] ALPINE-CVE-2017-17044

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-17044
Ecosystem: Alpine:v3.5, Alpine:v3.6
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17044
Type: osv

## Affected
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r2
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r2

## Details
An issue was discovered in Xen through 4.9.x allowing HVM guest OS users to cause a denial of service (infinite loop and host OS hang) by leveraging the mishandling of Populate on Demand (PoD) errors.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17044
