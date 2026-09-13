# [H] CVE-2019-19049

## Summary
Severity: High
Advisory: CVE-2019-19049
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19049
Type: osv

## Details
A memory leak in the unittest_data_add() function in drivers/of/unittest.c in the Linux kernel before 5.3.10 allows attackers to cause a denial of service (memory consumption) by triggering of_fdt_unflatten_tree() failures, aka CID-e13de8fe0d6a. NOTE: third parties dispute the relevance of this because unittest.c can only be reached during boot

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.10
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://bugzilla.suse.com/show_bug.cgi?id=1157173
- https://github.com/torvalds/linux/commit/e13de8fe0d6a51341671bbe384826d527afe8d44
