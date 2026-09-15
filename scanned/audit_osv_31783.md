# [M] iommu: Fix potential memory leak in iopf_queue_remove_device()

## Summary
Severity: Medium
Advisory: CVE-2025-21770
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21770
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu: Fix potential memory leak in iopf_queue_remove_device()

The iopf_queue_remove_device() helper removes a device from the per-iommu
iopf queue when PRI is disabled on the device. It responds to all
outstanding iopf's with an IOMMU_PAGE_RESP_INVALID code and detaches the
device from the queue.

However, it fails to release the group structure that represents a group
of iopf's awaiting for a response after responding to the hardware. This
can cause a memory leak if iopf_queue_remove_device() is called with
pending iopf's.

Fix it by calling iopf_free_group() after the iopf group is responded.

## References
- https://git.kernel.org/stable/c/90d5429cd2921ca2714684ed525898d431bb9283
- https://git.kernel.org/stable/c/9759ae2cee7cd42b95f1c48aa3749bd02b5ddb08
- https://git.kernel.org/stable/c/db60d2d896a17decd58d143eef92cf22eb0a0176
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21770.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21770
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
