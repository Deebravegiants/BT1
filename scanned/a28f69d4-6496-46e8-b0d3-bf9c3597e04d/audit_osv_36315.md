# [H] arp: do not assume dev_hard_header() does not change skb->head

## Summary
Severity: High
Advisory: CVE-2026-22988
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-22988
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.160 <6.1.161, >=6.6.120 <6.6.121, >=6.12.64 <6.12.66, >=6.18.4 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

arp: do not assume dev_hard_header() does not change skb->head

arp_create() is the only dev_hard_header() caller
making assumption about skb->head being unchanged.

A recent commit broke this assumption.

Initialize @arp pointer after dev_hard_header() call.

## References
- https://git.kernel.org/stable/c/029935507d0af6553c45380fbf6feecf756fd226
- https://git.kernel.org/stable/c/393525dee5c39acff8d6705275d7fcaabcfb7f0a
- https://git.kernel.org/stable/c/70bddc16491ef4681f3569b3a2c80309a3edcdd1
- https://git.kernel.org/stable/c/949647e7771a4a01963fe953a96d81fba7acecf3
- https://git.kernel.org/stable/c/c92510f5e3f82ba11c95991824a41e59a9c5ed81
- https://git.kernel.org/stable/c/dd6ccec088adff4bdf33e2b2dd102df20a7128fa
- https://git.kernel.org/stable/c/e432dbff342b95fe44645f9a90fcf333c80f4b5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22988.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
