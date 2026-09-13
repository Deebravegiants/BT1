# [H] ALPINE-CVE-2019-17347

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-17347
Ecosystem: Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17347
Type: osv

## Affected
- Alpine:v3.9: `xen` — affected >=4.1.0 <4.11.2-r0

## Details
An issue was discovered in Xen through 4.11.x allowing x86 PV guest OS users to cause a denial of service or gain privileges because a guest can manipulate its virtualised %cr4 in a way that is incompatible with Linux (and possibly other guest kernels).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17347
