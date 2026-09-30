# [M] ALPINE-CVE-2024-45818

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-45818
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45818
Type: osv

## Affected
- Alpine:v3.17: `xen` — affected >=4.6.0 <4.16.6-r3
- Alpine:v3.18: `xen` — affected >=4.6.0 <4.17.5-r2
- Alpine:v3.19: `xen` — affected >=4.6.0 <4.18.3-r2
- Alpine:v3.20: `xen` — affected >=4.6.0 <4.18.3-r2
- Alpine:v3.21: `xen` — affected >=4.6.0 <4.19.0-r1
- Alpine:v3.22: `xen` — affected >=4.6.0 <4.19.0-r1
- Alpine:v3.23: `xen` — affected >=4.6.0 <4.19.0-r1
- Alpine:v3.24: `xen` — affected >=4.6.0 <4.19.0-r1

## Details
The hypervisor contains code to accelerate VGA memory accesses for HVM
guests, when the (virtual) VGA is in "standard" mode.  Locking involved
there has an unusual discipline, leaving a lock acquired past the
return from the function that acquired it.  This behavior results in a
problem when emulating an instruction with two memory accesses, both of
which touch VGA memory (plus some further constraints which aren't
relevant here).  When emulating the 2nd access, the lock that is already
being held would be attempted to be re-acquired, resulting in a
deadlock.

This deadlock was already found when the code was first introduced, but
was analysed incorrectly and the fix was incomplete.  Analysis in light
of the new finding cannot find a way to make the existing locking
discipline work.

In staging, this logic has all been removed because it was discovered
to be accidentally disabled since Xen 4.7.  Therefore, we are fixing the
locking problem by backporting the removal of most of the feature.  Note
that even with the feature disabled, the lock would still be acquired
for any accesses to the VGA MMIO region.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45818
