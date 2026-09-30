# [M] ALPINE-CVE-2022-33744

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-33744
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-33744
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=0 <4.15.4-r0

## Details
Arm guests can cause Dom0 DoS via PV devices When mapping pages of guests on Arm, dom0 is using an rbtree to keep track of the foreign mappings. Updating of that rbtree is not always done completely with the related lock held, resulting in a small race window, which can be used by unprivileged guests via PV devices to cause inconsistencies of the rbtree. These inconsistencies can lead to Denial of Service (DoS) of dom0, e.g. by causing crashes or the inability to perform further mappings of other guests' memory pages.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-33744
