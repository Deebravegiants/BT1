# [H] netfilter: nft_set_pipapo: walk over current view on netlink dump

## Summary
Severity: High
Advisory: CVE-2024-27017
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27017
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.112, >=6.2.0 <6.6.53, >=6.4.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_pipapo: walk over current view on netlink dump

The generation mask can be updated while netlink dump is in progress.
The pipapo set backend walk iterator cannot rely on it to infer what
view of the datastructure is to be used. Add notation to specify if user
wants to read/update the set.

Based on patch from Florian Westphal.

## References
- https://git.kernel.org/stable/c/29b359cf6d95fd60730533f7f10464e95bd17c73
- https://git.kernel.org/stable/c/52735a010f37580b3a569a996f878fdd87425650
- https://git.kernel.org/stable/c/721715655c72640567e8742567520c99801148ed
- https://git.kernel.org/stable/c/ce9fef54c5ec9912a0c9a47bac3195cc41b14679
- https://git.kernel.org/stable/c/f24d8abc2bb8cbf31ec713336e402eafa8f42f60
- https://git.kernel.org/stable/c/ff89db14c63a827066446460e39226c0688ef786
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27017.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27017
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
