# [M] ALPINE-CVE-2023-46841

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-46841
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46841
Type: osv

## Affected
- Alpine:v3.16: `xen` — affected >=4.14.0 <4.16.5-r7
- Alpine:v3.17: `xen` — affected >=4.14.0 <4.16.5-r7
- Alpine:v3.18: `xen` — affected >=4.14.0 <4.17.3-r1
- Alpine:v3.19: `xen` — affected >=4.14.0 <4.18.0-r4
- Alpine:v3.20: `xen` — affected >=4.14.0 <4.18.0-r4
- Alpine:v3.21: `xen` — affected >=4.14.0 <4.18.0-r4
- Alpine:v3.22: `xen` — affected >=4.14.0 <4.18.0-r4
- Alpine:v3.23: `xen` — affected >=4.14.0 <4.18.0-r4
- Alpine:v3.24: `xen` — affected >=4.14.0 <4.18.0-r4

## Details
Recent x86 CPUs offer functionality named Control-flow Enforcement
Technology (CET).  A sub-feature of this are Shadow Stacks (CET-SS).
CET-SS is a hardware feature designed to protect against Return Oriented
Programming attacks. When enabled, traditional stacks holding both data
and return addresses are accompanied by so called "shadow stacks",
holding little more than return addresses.  Shadow stacks aren't
writable by normal instructions, and upon function returns their
contents are used to check for possible manipulation of a return address
coming from the traditional stack.

In particular certain memory accesses need intercepting by Xen.  In
various cases the necessary emulation involves kind of replaying of
the instruction.  Such replaying typically involves filling and then
invoking of a stub.  Such a replayed instruction may raise an
exceptions, which is expected and dealt with accordingly.

Unfortunately the interaction of both of the above wasn't right:
Recovery involves removal of a call frame from the (traditional) stack.
The counterpart of this operation for the shadow stack was missing.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46841
