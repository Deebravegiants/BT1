# [M] CVE-2022-1184

## Summary
Severity: Medium
Advisory: CVE-2022-1184
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-1184
Type: osv

## Details
A use-after-free flaw was found in fs/ext4/namei.c:dx_insert_block() in the Linux kernel’s filesystem sub-component. This flaw allows a local attacker with a user privilege to cause a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2022-1184
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://www.debian.org/security/2022/dsa-5257
- https://bugzilla.redhat.com/show_bug.cgi?id=2070205
- https://ubuntu.com/security/CVE-2022-1184
