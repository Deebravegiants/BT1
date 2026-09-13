# [M] CVE-2021-33624

## Summary
Severity: Medium
Advisory: CVE-2021-33624
Aliases: A-192972537, PUB-A-192972537
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-23
Source: https://osv.dev/vulnerability/CVE-2021-33624
Type: osv

## Details
In kernel/bpf/verifier.c in the Linux kernel before 5.12.13, a branch can be mispredicted (e.g., because of type confusion) and consequently an unprivileged BPF program can read arbitrary memory locations via a side-channel attack, aka CID-9183671af6db.

## References
- https://www.usenix.org/conference/usenixsecurity21/presentation/kirzner
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://github.com/torvalds/linux/commit/9183671af6dbf60a1219371d4ed73e23f43b49db
- https://github.com/benschlueter/CVE-2021-33624
- http://www.openwall.com/lists/oss-security/2021/06/21/1
