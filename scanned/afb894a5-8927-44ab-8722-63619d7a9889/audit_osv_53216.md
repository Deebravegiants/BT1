# [M] CVE-2022-33744

## Summary
Severity: Medium
Advisory: CVE-2022-33744
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/CVE-2022-33744
Type: osv

## Details
Arm guests can cause Dom0 DoS via PV devices When mapping pages of guests on Arm, dom0 is using an rbtree to keep track of the foreign mappings. Updating of that rbtree is not always done completely with the related lock held, resulting in a small race window, which can be used by unprivileged guests via PV devices to cause inconsistencies of the rbtree. These inconsistencies can lead to Denial of Service (DoS) of dom0, e.g. by causing crashes or the inability to perform further mappings of other guests' memory pages.

## References
- https://www.debian.org/security/2022/dsa-5191
- https://xenbits.xenproject.org/xsa/advisory-406.txt
- https://lists.debian.org/debian-lts-announce/2022/10/msg00000.html
- http://www.openwall.com/lists/oss-security/2022/07/05/4
- http://xenbits.xen.org/xsa/advisory-406.html
