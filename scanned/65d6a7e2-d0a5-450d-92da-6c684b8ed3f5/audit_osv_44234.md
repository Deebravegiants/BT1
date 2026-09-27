# [H] netfilter: synproxy: fix unaligned memory access in timestamp adjustment

## Summary
Severity: High
Advisory: CVE-2026-80637
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80637
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: synproxy: fix unaligned memory access in timestamp adjustment

Use get_unaligned_be32() and put_unaligned_be32() to safely read and
write the timestamp fields. This prevents performance degradation due to
unaligned memory access or even a crash on strict alignment
architectures.

This follows the implementation of timestamp parsing in the networking
stack at tcp_parse_options() and synproxy_parse_options().

## References
- https://git.kernel.org/stable/c/2b8e7aaa38002d8ee2f48d87b1f392eadd8e98c4
- https://git.kernel.org/stable/c/5c9c67cf7a3d16051dfb90e98836f530964dfb8e
- https://git.kernel.org/stable/c/992c20bc8a4aba220c8b95b467d049289778dad6
- https://git.kernel.org/stable/c/ea3d2caa5bfacf5db5c1cad521ca5d9144edd9a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80637.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80637
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
