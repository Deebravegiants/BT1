# [M] CVE-2019-19036

## Summary
Severity: Medium
Advisory: CVE-2019-19036
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-21
Source: https://osv.dev/vulnerability/CVE-2019-19036
Type: osv

## Details
btrfs_root_node in fs/btrfs/ctree.c in the Linux kernel through 5.3.12 allows a NULL pointer dereference because rcu_dereference(root->node) can be zero.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://usn.ubuntu.com/4414-1/
- https://usn.ubuntu.com/4439-1/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19036
