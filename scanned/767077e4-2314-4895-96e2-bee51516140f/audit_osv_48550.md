# [M] CVE-2017-9242

## Summary
Severity: Medium
Advisory: CVE-2017-9242
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-27
Source: https://osv.dev/vulnerability/CVE-2017-9242
Type: osv

## Details
The __ip6_append_data function in net/ipv6/ip6_output.c in the Linux kernel through 4.11.3 is too late in checking whether an overwrite of an skb data structure may occur, which allows local users to cause a denial of service (system crash) via crafted system calls.

## References
- https://patchwork.ozlabs.org/patch/764880/
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- http://www.debian.org/security/2017/dsa-3886
- http://www.securityfocus.com/bid/98731
- https://github.com/torvalds/linux/commit/232cd35d0804cc241eb887bb8d4d9b3b9881c64a
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=232cd35d0804cc241eb887bb8d4d9b3b9881c64a
