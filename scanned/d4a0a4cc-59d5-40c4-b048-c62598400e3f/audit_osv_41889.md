# [C] net: tls: prevent chain-after-chain in plain text SG

## Summary
Severity: Critical
Advisory: CVE-2026-64046
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64046
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tls: prevent chain-after-chain in plain text SG

Sashiko points out that if end = 0 (start != 0) the current
code will create a chain link to content type right after
the wrap link:

  This would create a chain where the wrap link points directly
  to another chain link. The scatterlist API sg_next iterator
  does not recursively resolve consecutive chain links.

meaning this is illegal input to crypto.

The wrapping link is unnecessary if end = 0. end is the entry after
the last one used so end = 0 means there's nothing pushed after
the wrap:

   end         start            i
    v            v              v
  [   ]...[   ][ d ][ d ][ d ][ d ][rsv for wrap]

Skip the wrapping in this case.

TLS 1.3 can use the "wrapping slot" for it's chaining if end = 0.
This avoids the chain-after-chain.

Move the wrap chaining before marking END and chaining off content
type, that feels like more logical ordering to me, but should not
matter from functional perspective.

## References
- https://git.kernel.org/stable/c/410351158dfef2d67fea6603680b3a6013c6ed9d
- https://git.kernel.org/stable/c/49a5faaa471ddcd37b6893970c9916eb836e7c31
- https://git.kernel.org/stable/c/91359966e247c0244c66d50bbb8e74aefa4321c3
- https://git.kernel.org/stable/c/929b1548e63ac72e104c07d8ee8cbbeeba2fa89a
- https://git.kernel.org/stable/c/acdc12b71c9aa4be5dcd2c8062753c6d2033e235
- https://git.kernel.org/stable/c/af855f4c966afafef74faf8390c7b86568c0d46d
- https://git.kernel.org/stable/c/b9c015ef1a7bf1e8dc67f21c6381f36deb2c3a36
- https://git.kernel.org/stable/c/ff26a0e8377dec07e4a7230db7675bed1b9a6d03
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64046.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64046
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
