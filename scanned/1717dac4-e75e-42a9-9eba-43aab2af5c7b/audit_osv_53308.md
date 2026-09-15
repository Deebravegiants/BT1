# [M] CVE-2022-3707

## Summary
Severity: Medium
Advisory: CVE-2022-3707
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2022-3707
Type: osv

## Details
A double-free memory flaw was found in the Linux kernel. The Intel GVT-g graphics driver triggers VGA card system resource overload, causing a fail in the intel_gvt_dma_map_guest_page function. This issue could allow a local user to crash the system.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://lore.kernel.org/all/20221007013708.1946061-1-zyytlz.wz%40163.com/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2137979
