# [H] net: openvswitch: fix nested key length validation in the set() action

## Summary
Severity: High
Advisory: CVE-2025-37789
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37789
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: openvswitch: fix nested key length validation in the set() action

It's not safe to access nla_len(ovs_key) if the data is smaller than
the netlink header.  Check that the attribute is OK first.

## References
- https://git.kernel.org/stable/c/03d7262dd53e8c404da35cc81aaa887fd901f76b
- https://git.kernel.org/stable/c/1489c195c8eecd262aa6712761ba5288203e28ec
- https://git.kernel.org/stable/c/54c6957d1123a2032099b9eab51c314800f677ce
- https://git.kernel.org/stable/c/65d91192aa66f05710cfddf6a14b5a25ee554dba
- https://git.kernel.org/stable/c/7fcaec0b2ab8fa5fbf0b45e5512364a168f445bd
- https://git.kernel.org/stable/c/824a7c2df5127b2402b68a21a265d413e78dcad7
- https://git.kernel.org/stable/c/a27526e6b48eee9e2d82efff502c4f272f1a91d4
- https://git.kernel.org/stable/c/be80768d4f3b6fd13f421451cc3fee8778aba8bc
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37789.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37789
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
