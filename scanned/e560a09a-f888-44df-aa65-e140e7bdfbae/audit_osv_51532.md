# [M] CVE-2021-31829

## Summary
Severity: Medium
Advisory: CVE-2021-31829
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-31829
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 5.12.1 performs undesirable speculative loads, leading to disclosure of stack content via side-channel attacks, aka CID-801c6058d14a. The specific concern is not protecting the BPF stack area against speculative loads. Also, the BPF stack can contain uninitialized data that might represent sensitive information previously operated on by the kernel.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VWCZ6LJLENL2C3URW5ICARTACXPFCFN2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y4X2G5YAPYJGI3PFEZZNOTRYI33GOCCZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZI7OBCJQDNWMKLBP6MZ5NV4EUTDAMX6Q/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- http://www.openwall.com/lists/oss-security/2021/05/04/4
- https://github.com/torvalds/linux/commit/801c6058d14a82179a7ee17a4b532cac6fad067f
