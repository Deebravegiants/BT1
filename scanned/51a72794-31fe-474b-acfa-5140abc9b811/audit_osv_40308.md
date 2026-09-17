# [H] batman-adv: tvlv: reject oversized TVLV packets

## Summary
Severity: High
Advisory: CVE-2026-52934
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52934
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: tvlv: reject oversized TVLV packets

batadv_tvlv_container_ogm_append() builds a TVLV packet section from
the tvlv.container_list. The total size of this section is computed by
batadv_tvlv_container_list_size(), which sums the sizes of all registered
containers.

The return type and accumulator in batadv_tvlv_container_list_size() were
u16. If the accumulated size exceeds U16_MAX, the value wraps around,
causing the subsequent allocation in batadv_tvlv_container_ogm_append()
to be undersized. The memcpy-style copy that follows would then write
beyond the end of the allocated buffer, corrupting kernel memory.

Fix this by widening the return type of batadv_tvlv_container_list_size()
to size_t. In batadv_tvlv_container_ogm_append(), check the computed length
against U16_MAX before proceeding, and bail out as if the allocation had
failed when the limit is exceeded.

## References
- https://git.kernel.org/stable/c/13493b00dd1e05a705981e052158652ea23eb482
- https://git.kernel.org/stable/c/1595628a2f877d052eda18865ccf539392c47c04
- https://git.kernel.org/stable/c/6448a49344e87487b61bd88cb850cd694a0f576d
- https://git.kernel.org/stable/c/94a3d72cd9b21116d7c6d5bdc57c11401fc28557
- https://git.kernel.org/stable/c/94db72e9dac202e017ee3db22c59d17e4f3bf171
- https://git.kernel.org/stable/c/c02aa6c0c9d1bea9bb75dea362b75ad225137bae
- https://git.kernel.org/stable/c/ede47988ac5687793745b17c1634a496a2299919
- https://git.kernel.org/stable/c/f50487e3566358b2b982b7801945e858c78ad9ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52934.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52934
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
