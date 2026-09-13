# [H] iommu/vt-d: Fix race condition during PASID entry replacement

## Summary
Severity: High
Advisory: CVE-2026-45945
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45945
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.39, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Fix race condition during PASID entry replacement

The Intel VT-d PASID table entry is 512 bits (64 bytes). When replacing
an active PASID entry (e.g., during domain replacement), the current
implementation calculates a new entry on the stack and copies it to the
table using a single structure assignment.

        struct pasid_entry *pte, new_pte;

        pte = intel_pasid_get_entry(dev, pasid);
        pasid_pte_config_first_level(iommu, &new_pte, ...);
        *pte = new_pte;

Because the hardware may fetch the 512-bit PASID entry in multiple
128-bit chunks, updating the entire entry while it is active (Present
bit set) risks a "torn" read. In this scenario, the IOMMU hardware
could observe an inconsistent state — partially new data and partially
old data — leading to unpredictable behavior or spurious faults.

Fix this by removing the unsafe "replace" helpers and following the
"clear-then-update" flow, which ensures the Present bit is cleared and
the required invalidation handshake is completed before the new
configuration is applied.

## References
- https://git.kernel.org/stable/c/4718007870547e1efebbdd6745d9fce58f008fef
- https://git.kernel.org/stable/c/66a7aff480a82b8642b3991fed5fdc9780022157
- https://git.kernel.org/stable/c/c3b1edea3791fa91ab7032faa90355913ad9451b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45945.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45945
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
