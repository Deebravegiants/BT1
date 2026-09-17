# [C] dm-verity: fix buffer overflow in FEC calculation

## Summary
Severity: Critical
Advisory: CVE-2026-72098
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72098
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-verity: fix buffer overflow in FEC calculation

There's a buffer overflow in dm-verity-fec:

if (neras && *neras <= v->fec->roots)
	fio->erasures[(*neras)++] = i;

This allows *neras to reach roots + 1 (the post-increment pushes it past
roots). This value is then passed as no_eras to decode_rs8(). Inside the
RS decoder (lib/reed_solomon/decode_rs.c:113-121), the erasure locator
polynomial loop writes lambda[j] where j can reach nroots + 1 — one
element past the end of lambda[] (which is sized nroots + 1, valid
indices 0..nroots). The out-of-bounds write lands on syn[0], corrupting
the syndrome buffer.

## References
- https://git.kernel.org/stable/c/31d6e6c0ba8d5a7bd59660035a089307100c5e8e
- https://git.kernel.org/stable/c/5488d3a69d205e28f74f18857b853aa12e778e66
- https://git.kernel.org/stable/c/f7990c2b0f08b8841fcd2652d1d7002f5994a7a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72098.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72098
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
