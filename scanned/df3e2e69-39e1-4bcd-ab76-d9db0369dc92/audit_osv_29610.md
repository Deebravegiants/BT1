# [H] mptcp: pm: avoid possible UaF when selecting endp

## Summary
Severity: High
Advisory: CVE-2024-44974
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44974
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.109, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: pm: avoid possible UaF when selecting endp

select_local_address() and select_signal_address() both select an
endpoint entry from the list inside an RCU protected section, but return
a reference to it, to be read later on. If the entry is dereferenced
after the RCU unlock, reading info could cause a Use-after-Free.

A simple solution is to copy the required info while inside the RCU
protected section to avoid any risk of UaF later. The address ID might
need to be modified later to handle the ID0 case later, so a copy seems
OK to deal with.

## References
- https://git.kernel.org/stable/c/0201d65d9806d287a00e0ba96f0321835631f63f
- https://git.kernel.org/stable/c/2b4f46f9503633dade75cb796dd1949d0e6581a1
- https://git.kernel.org/stable/c/48e50dcbcbaaf713d82bf2da5c16aeced94ad07d
- https://git.kernel.org/stable/c/9a9afbbc3fbfca4975eea4aa5b18556db5a0c0b8
- https://git.kernel.org/stable/c/ddee5b4b6a1cc03c1e9921cf34382e094c2009f1
- https://git.kernel.org/stable/c/f2c865e9e3ca44fc06b5f73b29a954775e4dbb38
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44974.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44974
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
