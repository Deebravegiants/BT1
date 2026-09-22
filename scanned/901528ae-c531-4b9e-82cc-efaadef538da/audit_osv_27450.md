# [M] OOB Access in CefLayeredWindowUpdaterOSR::OnAllocatedSharedMemory

## Summary
Severity: Medium
Advisory: CVE-2024-21639
Aliases: GHSA-m375-jw5x-x8mg
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2024-21639
Type: osv

## Details
CEF (Chromium Embedded Framework ) is a simple framework for embedding Chromium-based browsers in other applications. `CefLayeredWindowUpdaterOSR::OnAllocatedSharedMemory` does not check the size of the shared memory, which leads to out-of-bounds read outside the sandbox. This vulnerability was patched in commit 1f55d2e.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21639.json
- https://github.com/chromiumembedded/cef/security/advisories/GHSA-m375-jw5x-x8mg
- https://nvd.nist.gov/vuln/detail/CVE-2024-21639
- https://github.com/chromiumembedded/cef/commit/1f55d2e12f62cfdfbf9da6968fde2f928982670b
