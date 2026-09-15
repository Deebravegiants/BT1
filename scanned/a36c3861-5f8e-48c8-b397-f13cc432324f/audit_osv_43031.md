# [C] gue: validate REMCSUM private option length

## Summary
Severity: Critical
Advisory: CVE-2026-72351
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72351
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

gue: validate REMCSUM private option length

GUE private flags can indicate that remote checksum offload metadata is
present. The private flags field itself is accounted for by
guehdr_flags_len(), but guehdr_priv_flags_len() currently returns 0 even
when GUE_PFLAG_REMCSUM is set.

This lets a packet with only the private flags field pass
validate_gue_flags(), after which gue_remcsum() and gue_gro_remcsum()
read the missing REMCSUM start/offset fields from the following bytes.

Account for GUE_PLEN_REMCSUM when GUE_PFLAG_REMCSUM is present so that
malformed packets are rejected during option validation.

## References
- https://git.kernel.org/stable/c/158b9995d3c87f3b93f5c22df54a12e12a3438b3
- https://git.kernel.org/stable/c/2a99224c120823987e4d829726f4ecb33e03fc1e
- https://git.kernel.org/stable/c/2c4de9988e9ddc760b750d6b6e701c35ff60ad14
- https://git.kernel.org/stable/c/4a4a1d41c6e901e773bcf795f562a47fa71f692a
- https://git.kernel.org/stable/c/61e78679c7c9ca685bff58e4b6348304dc60aafd
- https://git.kernel.org/stable/c/7c6876ec1b227261b51803f784c7be1b2242a1a0
- https://git.kernel.org/stable/c/d335dcc6f521571d57117b8deeebc940836e5450
- https://git.kernel.org/stable/c/f618cbe9b24cd0202004d2db781d5f80ab77037f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72351.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72351
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
