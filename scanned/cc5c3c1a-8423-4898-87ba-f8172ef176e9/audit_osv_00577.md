# [H] ALPINE-CVE-2017-17045

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-17045
Ecosystem: Alpine:v3.5, Alpine:v3.6
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17045
Type: osv

## Affected
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r2
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r2

## Details
An issue was discovered in Xen through 4.9.x allowing HVM guest OS users to gain privileges on the host OS, obtain sensitive information, or cause a denial of service (BUG and host OS crash) by leveraging the mishandling of Populate on Demand (PoD) Physical-to-Machine (P2M) errors.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17045
