# [H] ALPINE-CVE-2017-8905

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-8905
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8905
Type: osv

## Affected
- Alpine:v3.3: `xen` — affected >=0 <4.6.3-r7
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r9
- Alpine:v3.5: `xen` — affected >=0 <4.7.2-r1

## Details
Xen through 4.6.x on 64-bit platforms mishandles a failsafe callback, which might allow PV guest OS users to execute arbitrary code on the host OS, aka XSA-215.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8905
