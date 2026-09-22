# [M] CVE-2021-3428

## Summary
Severity: Medium
Advisory: CVE-2021-3428
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/CVE-2021-3428
Type: osv

## Details
A flaw was found in the Linux kernel. A denial of service problem is identified if an extent tree is corrupted in a crafted ext4 filesystem in fs/ext4/extents.c in ext4_es_cache_extent. Fabricating an integer overflow, A local attacker with a special user privilege may cause a system crash problem which can lead to an availability threat.

## References
- https://ubuntu.com/security/CVE-2021-3428
- https://www.openwall.com/lists/oss-security/2021/03/17/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1972621
