# [H] iommu/iommufd: Fix IOPF group ownership UAF

## Summary
Severity: High
Advisory: CVE-2026-74520
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74520
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/iommufd: Fix IOPF group ownership UAF

iopf_group_alloc() links each last-page IOPF group into the generic IOPF
pending list before invoking the domain fault handler.
iommufd_fault_iopf_handler() also queued an accepted group in the
IOMMUFD deliver list without removing it from the generic pending list.

When detach or HWPT replacement drops the device's IOPF reference count
to zero, an IOMMU driver may call iopf_queue_remove_device(). That
function responds to and frees groups through the generic pending list
without removing the same groups from IOMMUFD's deliver list or response
xarray. A later read, response, or cleanup can then access the freed
group and cause a UAF.

Fix this by dequeuing an accepted group from the generic pending list
before IOMMUFD queues it for userspace response.
Make iopf_group_response() send a response regardless of pending-list
membership, so the dequeued group can still be completed by IOMMUFD.

## References
- https://git.kernel.org/stable/c/4e74a369236424114b94cf6a9f5ff9e848b430b4
- https://git.kernel.org/stable/c/6da8f37419dd4c456f26fc203f04e000186f4b3d
- https://git.kernel.org/stable/c/738e6f32e61d80b554e37015ecb7bc620b88001c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74520.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74520
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
