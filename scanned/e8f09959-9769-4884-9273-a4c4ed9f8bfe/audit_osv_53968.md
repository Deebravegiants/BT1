# [H] CVE-2023-34326

## Summary
Severity: High
Advisory: CVE-2023-34326
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2023-34326
Type: osv

## Details
The caching invalidation guidelines from the AMD-Vi specification (48882—Rev
3.07-PUB—Oct 2022) is incorrect on some hardware, as devices will malfunction
(see stale DMA mappings) if some fields of the DTE are updated but the IOMMU
TLB is not flushed.

Such stale DMA mappings can point to memory ranges not owned by the guest, thus
allowing access to unindented memory regions.

## References
- https://xenbits.xenproject.org/xsa/advisory-442.html
