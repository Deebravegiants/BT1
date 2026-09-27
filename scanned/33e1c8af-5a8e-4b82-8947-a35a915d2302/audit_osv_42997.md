# [C] net: ife: require ETH_HLEN to be pullable in ife_decode()

## Summary
Severity: Critical
Advisory: CVE-2026-72296
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72296
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ife: require ETH_HLEN to be pullable in ife_decode()

ife decode may return after making only the outer IFE header and
metadata pullable. The caller then passes the decapsulated packet to
eth_type_trans(), which expects the inner Ethernet header to be
accessible from the linear data area.

With a malformed IFE frame, the inner Ethernet header may still be
shorter than ETH_HLEN in the linear area, which can lead to a crash in
the original code.

Fix this by extending the pull check in ife_decode() so that the inner
Ethernet header is also guaranteed to be pullable before returning.

## References
- https://git.kernel.org/stable/c/1cb42ec10294a55380e52e674b3df2b962648242
- https://git.kernel.org/stable/c/5526d1997aea6c9bd865ca4d4894b52e799d735c
- https://git.kernel.org/stable/c/70013f9163bef7fbd9fa62f81cf91b2a7ba66163
- https://git.kernel.org/stable/c/8c8818e52fddb247ff3214622401a4de6ff8482e
- https://git.kernel.org/stable/c/9406f6012b7343661efb516a11c62d4db2b62f75
- https://git.kernel.org/stable/c/9433578bff9c100c466a6354574892e55293cb8f
- https://git.kernel.org/stable/c/b69ad768cd4a2ef4e07c18492ae85438ed17c7cb
- https://git.kernel.org/stable/c/be272e159dfe1207b67332ad6e17adcf59b4ea4b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72296.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72296
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
