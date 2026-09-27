# [C] rtase: fix double free of multi-frag skb on DMA map failure

## Summary
Severity: Critical
Advisory: CVE-2026-74545
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74545
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtase: fix double free of multi-frag skb on DMA map failure

In rtase_start_xmit(), when the head buffer DMA mapping fails after
rtase_xmit_frags() has mapped all fragments, the error path clears
the fragment descriptors with rtase_tx_clear_range(), which frees
the skb through the last-frag slot and accounts tx_dropped. Control
then falls through to the common error label, which frees the same
skb a second time and counts it again.

Return right after clearing the fragments when the skb owns frags;
the no-frag case still drops through and frees the head skb once.

## References
- https://git.kernel.org/stable/c/4f09172aff5f73a5e914f4fbc0d00a1c2ea9f7cb
- https://git.kernel.org/stable/c/6fb7b769d6ed6d1d2e02af4a80e57a2477f35086
- https://git.kernel.org/stable/c/db986098f30881fafcc752800aa3b13fd289c922
- https://git.kernel.org/stable/c/de691dc3227b061c4d0beba9f0128fe1ff33dd68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74545.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74545
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
