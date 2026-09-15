# [H] net: xilinx: axienet: Add error handling for RX metadata pointer retrieval

## Summary
Severity: High
Advisory: CVE-2025-39897
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39897
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: xilinx: axienet: Add error handling for RX metadata pointer retrieval

Add proper error checking for dmaengine_desc_get_metadata_ptr() which
can return an error pointer and lead to potential crashes or undefined
behaviour if the pointer retrieval fails.

Properly handle the error by unmapping DMA buffer, freeing the skb and
returning early to prevent further processing with invalid data.

## References
- https://git.kernel.org/stable/c/8bbceba7dc5090c00105e006ce28d1292cfda8dd
- https://git.kernel.org/stable/c/92e2fc92bc4eb2bc0e84404316fbc02ddd0a3196
- https://git.kernel.org/stable/c/d0ecda6fdd840b406df6617b003b036f65dd8926
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39897.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39897
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
