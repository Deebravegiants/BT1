# [H] netfilter: nft_payload: fix mask build for partial field offload

## Summary
Severity: High
Advisory: CVE-2026-74579
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74579
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_payload: fix mask build for partial field offload

nft_payload_offload_mask() builds the offload match mask for a payload
expression that covers only part of a header field.  For a partial IPv6
address match (field_len = 16, priv_len = 1) that shift is 1 << 120, which
is undefined on the 32-bit int operand.  It also trims only one word, so
the remaining words stay 0xffffffff (and when priv_len is a multiple of 4
the trim is skipped entirely), leaving the mask covering more bytes than
the rule matches.

  UBSAN: shift-out-of-bounds in net/netfilter/nft_payload.c:278:20
  shift exponent 120 is too large for 32-bit type 'int'
  ...

The match is byte-granular and struct nft_data is zero-initialised, so the
correct mask is simply the first priv_len bytes set to 0xff. Set those
bytes directly and drop the word/shift trimming; this removes the undefined
shift and no longer over-masks the trailing bytes.

## References
- https://git.kernel.org/stable/c/16b553c46e347bc9de9946c4960654d5884a86de
- https://git.kernel.org/stable/c/363c3a84a946d53e5e121c9f47c7c2b7d228c46b
- https://git.kernel.org/stable/c/39e88f28fb32bf02bd4b525c24c842c9cff5663d
- https://git.kernel.org/stable/c/3ee7b3f813b11f28cd6efdf7f24d64b5a7fd4dc7
- https://git.kernel.org/stable/c/630295d5bba1d0e0f494cc459452eb0a0058c545
- https://git.kernel.org/stable/c/8720df4504e0ed1781a702f65251bd47b3534d5e
- https://git.kernel.org/stable/c/a375d8ace807767f29f276b681b6324c74929b1d
- https://git.kernel.org/stable/c/b19b5d2e042c294e2cc1c908dc598f9d64015396
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74579.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74579
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
