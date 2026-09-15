# [M] CVE-2021-34556

## Summary
Severity: Medium
Advisory: CVE-2021-34556
Aliases: A-196011539, PUB-A-196011539
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-02
Source: https://osv.dev/vulnerability/CVE-2021-34556
Type: osv

## Details
In the Linux kernel through 5.13.7, an unprivileged BPF program can obtain sensitive information from kernel memory via a Speculative Store Bypass side-channel attack because the protection mechanism neglects the possibility of uninitialized memory locations on the BPF stack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6JKK6XNRZX5BT5QVYOKGVJ2BHFZAP5EX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/565ZS55ZFEN62WVRRORT7R63RXW5F4T4/
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/patch/?id=2039f26f3aca5b0e419b98f65dd36481337b86ee
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/patch/?id=f5e81d1117501546b7be050c5fbafa6efd2c722c
- http://www.openwall.com/lists/oss-security/2021/08/01/3
