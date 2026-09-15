# [H] CVE-2023-1838

## Summary
Severity: High
Advisory: CVE-2023-1838
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-1838
Type: osv

## Details
A use-after-free flaw was found in vhost_net_set_backend in drivers/vhost/net.c in virtio network subcomponent in the Linux kernel due to a double fget. This flaw could allow a local attacker to crash the system, and could even lead to a kernel information leak problem.

## References
- https://lore.kernel.org/netdev/20220516084213.26854-1-jasowang%40redhat.com/T/
- https://security.netapp.com/advisory/ntap-20230517-0003/
