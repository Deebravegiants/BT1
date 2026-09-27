# [H] bpf: Check validity of link->type in bpf_link_show_fdinfo()

## Summary
Severity: High
Advisory: CVE-2024-53099
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-11-25
Source: https://osv.dev/vulnerability/CVE-2024-53099
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.123, >=6.2.0 <6.6.62, >=6.7.0 <6.11.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Check validity of link->type in bpf_link_show_fdinfo()

If a newly-added link type doesn't invoke BPF_LINK_TYPE(), accessing
bpf_link_type_strs[link->type] may result in an out-of-bounds access.

To spot such missed invocations early in the future, checking the
validity of link->type in bpf_link_show_fdinfo() and emitting a warning
when such invocations are missed.

## References
- https://git.kernel.org/stable/c/24fec234d2ba9ca3c14e545ebe3fd6dcb47f074d
- https://git.kernel.org/stable/c/4e8074bb33d18f56af30a0252cb3606d27eb1c13
- https://git.kernel.org/stable/c/79f87a6ec39fb5968049a6775a528bf58b25c20a
- https://git.kernel.org/stable/c/8421d4c8762bd022cb491f2f0f7019ef51b4f0a7
- https://git.kernel.org/stable/c/b3eb1b6a9f745d6941b345f0fae014dc8bb06d36
- https://git.kernel.org/stable/c/d5092b0a1aaf35d77ebd8d33384d7930bec5cb5d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53099.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
