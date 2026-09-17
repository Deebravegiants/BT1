# [M] OOB Access in CefVideoConsumerOSR::OnFrameCaptured

## Summary
Severity: Medium
Advisory: CVE-2024-21640
Aliases: GHSA-3h3j-38xq-v7hh
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-01-13
Source: https://osv.dev/vulnerability/CVE-2024-21640
Type: osv

## Details
Chromium Embedded Framework (CEF) is a simple framework for embedding Chromium-based browsers in other applications.`CefVideoConsumerOSR::OnFrameCaptured` does not check `pixel_format` properly, which leads to out-of-bounds read out of the sandbox. This vulnerability was patched in commit 1f55d2e.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21640.json
- https://github.com/chromiumembedded/cef/security/advisories/GHSA-3h3j-38xq-v7hh
- https://nvd.nist.gov/vuln/detail/CVE-2024-21640
- https://github.com/chromiumembedded/cef/commit/1f55d2e12f62cfdfbf9da6968fde2f928982670b
