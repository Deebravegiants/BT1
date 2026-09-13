# [C] Cloud Hypervisor: Use-after-free in virtio-block Async I/O Completion

## Summary
Severity: Critical
Advisory: CVE-2026-45782
Aliases: GHSA-f47p-p25q-83rh
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-45782
Type: osv

## Details
Cloud Hypervisor is a Virtual Machine Monitor for Cloud workloads. From version 21.0 to before version 51.2, a guest can cause a use-after-free in the cloud-hypervisor process by submitting two virtio-block descriptor chains that reuse the same head_index while asynchronous block I/O is enabled (e.g. io_uring, aio). When the kernel completes the duplicate operation before the original, the completion path frees a bounce buffer that the kernel is still actively reading from or writing to, corrupting the freed memory. This issue has been patched in versions 51.2 and 52.0.

## References
- https://github.com/cloud-hypervisor/cloud-hypervisor/releases/tag/v51.2
- https://github.com/cloud-hypervisor/cloud-hypervisor/releases/tag/v52.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45782.json
- https://github.com/cloud-hypervisor/cloud-hypervisor/security/advisories/GHSA-f47p-p25q-83rh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45782
- https://github.com/cloud-hypervisor/cloud-hypervisor/commit/1314ac883c641f1045bbb06dec0de045a3894baa
- https://github.com/cloud-hypervisor/cloud-hypervisor/pull/8220
