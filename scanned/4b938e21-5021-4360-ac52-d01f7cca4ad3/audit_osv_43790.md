# [H] net: ngbe: fix NULL pointer dereference in non-MSI-X interrupt enabling

## Summary
Severity: High
Advisory: CVE-2026-74741
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74741
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ngbe: fix NULL pointer dereference in non-MSI-X interrupt enabling

In non-MSI-X mode (such as legacy INTx or single MSI), wx->msix_entry is
not allocated or initialized. Calling NGBE_INTR_MISC(wx) dereferences
wx->msix_entry->entry, leading to a NULL pointer dereference crash.

This issue was introduced by fixing the IRQ vector when the number of
VFs is 7. Fix the issue by explicitly checking `pdev->msix_enabled` to
determine the correct vector index.

Additionally, as a side fix, set the interrupt mask to BIT(0) for the
non-MSI-X fallback. In MSI/INTx mode, the MISC and queue interrupts
share vector 0, and the WX_PX_MISC_IVAR register is only valid in the
MSI-X case. Thus, BIT(0) is the correct mask for the miscellaneous cause
when MSI-X is disabled.

## References
- https://git.kernel.org/stable/c/0ab482b2195edc000262f0eae1cdcb416b8f335d
- https://git.kernel.org/stable/c/5f3a13e0bb5ebcc1ca2dfda42ea40b9f3c2be6ea
- https://git.kernel.org/stable/c/cef4c5b9aca24651d069adf9462b221df6a2a669
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74741.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74741
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
