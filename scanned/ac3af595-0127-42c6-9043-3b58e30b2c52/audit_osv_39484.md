# [H] iommu/vt-d: Clear Present bit before tearing down PASID entry

## Summary
Severity: High
Advisory: CVE-2026-45894
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45894
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Clear Present bit before tearing down PASID entry

The Intel VT-d Scalable Mode PASID table entry consists of 512 bits (64
bytes). When tearing down an entry, the current implementation zeros the
entire 64-byte structure immediately using multiple 64-bit writes.

Since the IOMMU hardware may fetch these 64 bytes using multiple
internal transactions (e.g., four 128-bit bursts), updating or zeroing
the entire entry while it is active (P=1) risks a "torn" read. If a
hardware fetch occurs simultaneously with the CPU zeroing the entry, the
hardware could observe an inconsistent state, leading to unpredictable
behavior or spurious faults.

Follow the "Guidance to Software for Invalidations" in the VT-d spec
(Section 6.5.3.3) by implementing the recommended ownership handshake:

1. Clear only the 'Present' (P) bit of the PASID entry.
2. Use a dma_wmb() to ensure the cleared bit is visible to hardware
   before proceeding.
3. Execute the required invalidation sequence (PASID cache, IOTLB, and
   Device-TLB flush) to ensure the hardware has released all cached
   references.
4. Only after the flushes are complete, zero out the remaining fields
   of the PASID entry.

Also, add a dma_wmb() in pasid_set_present() to ensure that all other
fields of the PASID entry are visible to the hardware before the Present
bit is set.

## References
- https://git.kernel.org/stable/c/75ed00055c059dedc47b5daaaa2f8a7a019138ff
- https://git.kernel.org/stable/c/821807c167b7b48a41b95b6607c6b9f97600f7d9
- https://git.kernel.org/stable/c/949d71666e9dd19f21e7b4b53a88cd2c5b902858
- https://git.kernel.org/stable/c/a84d30e8d2bacd21782a6481158b7c9c552f4868
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45894.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45894
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
