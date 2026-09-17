# [M] CVE-2022-3524

## Summary
Severity: Medium
Advisory: CVE-2022-3524
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-16
Source: https://osv.dev/vulnerability/CVE-2022-3524
Type: osv

## Details
A vulnerability was found in Linux Kernel. It has been declared as problematic. Affected by this vulnerability is the function ipv6_renew_options of the component IPv6 Handler. The manipulation leads to memory leak. The attack can be launched remotely. It is recommended to apply a patch to fix this issue. The identifier VDB-211021 was assigned to this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://vuldb.com/?id.211021
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3c52c6bb831f6335c176a0fc7214e26f43adbd11
