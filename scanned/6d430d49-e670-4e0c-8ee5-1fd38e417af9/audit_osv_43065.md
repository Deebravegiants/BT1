# [C] geneve: validate inner network offset in geneve_gro_complete()

## Summary
Severity: Critical
Advisory: CVE-2026-72407
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72407
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

geneve: validate inner network offset in geneve_gro_complete()

Even with both paths gated on gs->gro_hint, geneve_gro_complete()
re-derives the inner dispatch type and length from the packet and the
current gs->gro_hint, independently of geneve_gro_receive(). The two can
disagree if gs->gro_hint flips under a concurrent geneve_quiesce()/
geneve_unquiesce() (sk_user_data is NULL across a synchronize_net()), or if
the re-read option bytes differ from the ones receive parsed.

geneve_gro_receive() already records the inner network header position in
NAPI_GRO_CB()->inner_network_offset. Have geneve_gro_complete() compute the
offset it is about to dispatch at, adding ETH_HLEN in the ETH_P_TEB case
where eth_gro_complete() steps over the inner MAC header, and bail out if
it lands past inner_network_offset.

Use a lower bound rather than exact equality: between gh_len and the inner
L3 header, geneve_gro_receive() may also have pulled an inner VLAN tag
(vlan_gro_receive() advances the recorded offset past it), which only moves
inner_network_offset further out. A valid frame therefore always satisfies
inner_nh <= inner_network_offset, while a gh_len inflated by a hint
gro_receive() did not honour dispatches past the validated inner header,
i.e. the out-of-bounds completion. Only the latter is rejected.

## References
- https://git.kernel.org/stable/c/cbb0d30a1ad6fc9439b1dc9b4f5a7a9140d3b11f
- https://git.kernel.org/stable/c/e2087447f562692ff0cd08a0554d8d4ad083aa5c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72407.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72407
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
