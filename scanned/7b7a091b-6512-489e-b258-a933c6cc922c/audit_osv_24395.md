# [M] Qemu: pvrdma: out-of-bounds read in pvrdma_ring_next_elem_read()

## Summary
Severity: Medium
Advisory: CVE-2023-1544
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-03-23
Source: https://osv.dev/vulnerability/CVE-2023-1544
Type: osv

## Details
A flaw was found in the QEMU implementation of VMWare's paravirtual RDMA device. This flaw allows a crafted guest driver to allocate and initialize a huge number of page tables to be used as a ring of descriptors for CQ and async events, potentially leading to an out-of-bounds read and crash of QEMU.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00042.html
- https://lists.nongnu.org/archive/html/qemu-devel/2023-03/msg00206.html
- https://access.redhat.com/security/cve/CVE-2023-1544
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1544.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1544
- https://security.netapp.com/advisory/ntap-20230511-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2180364
- https://gitlab.com/qemu-project/qemu
