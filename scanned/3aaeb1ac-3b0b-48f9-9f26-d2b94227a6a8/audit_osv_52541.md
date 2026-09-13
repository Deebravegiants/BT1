# [M] CVE-2021-47559

## Summary
Severity: Medium
Advisory: CVE-2021-47559
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47559
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: Fix NULL pointer dereferencing in smc_vlan_by_tcpsk()

Coverity reports a possible NULL dereferencing problem:

in smc_vlan_by_tcpsk():
6. returned_null: netdev_lower_get_next returns NULL (checked 29 out of 30 times).
7. var_assigned: Assigning: ndev = NULL return value from netdev_lower_get_next.
1623                ndev = (struct net_device *)netdev_lower_get_next(ndev, &lower);
CID 1468509 (#1 of 1): Dereference null return value (NULL_RETURNS)
8. dereference: Dereferencing a pointer that might be NULL ndev when calling is_vlan_dev.
1624                if (is_vlan_dev(ndev)) {

Remove the manual implementation and use netdev_walk_all_lower_dev() to
iterate over the lower devices. While on it remove an obsolete function
parameter comment.

## References
- https://git.kernel.org/stable/c/587acad41f1bc48e16f42bb2aca63bf323380be8
- https://git.kernel.org/stable/c/bb851d0fb02547d03cd40106b5f2391c4fed6ed1
- https://git.kernel.org/stable/c/c94cbd262b6aa3b54d73a1ed1f9c0d19df57f4ff
