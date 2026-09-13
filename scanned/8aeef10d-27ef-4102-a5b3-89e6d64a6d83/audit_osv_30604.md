# [H] NFSD: Prevent NULL dereference in nfsd4_process_cb_update()

## Summary
Severity: High
Advisory: CVE-2024-53217
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53217
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Prevent NULL dereference in nfsd4_process_cb_update()

@ses is initialized to NULL. If __nfsd4_find_backchannel() finds no
available backchannel session, setup_callback_client() will try to
dereference @ses and segfault.

## References
- https://git.kernel.org/stable/c/03178cd8f67227015debb700123987fe96275cd1
- https://git.kernel.org/stable/c/0c3b0e326f838787d229314d4de83af9c53347e8
- https://git.kernel.org/stable/c/1e02c641c3a43c88cecc08402000418e15578d38
- https://git.kernel.org/stable/c/4a4ffc1aa9d618e41ad9151f40966e402e58a5a2
- https://git.kernel.org/stable/c/752a75811f27300fe8131b0a1efc91960f6f88e7
- https://git.kernel.org/stable/c/c5d90f9302742985a5078e42ac38de42c364c44a
- https://git.kernel.org/stable/c/cac1405e3ff6685a438e910ad719e0cf06af90ee
- https://git.kernel.org/stable/c/d9a0d1f6e15859ea7a86a327f28491e23deaaa62
- https://git.kernel.org/stable/c/eb51733ae5fc73d95bd857d5da26f9f65b202a79
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53217.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53217
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
