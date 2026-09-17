# [M] Denial of Service in fzf

## Summary
Severity: Medium
Advisory: CVE-2026-53433
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-53433
Type: osv

## Details
fzf is vulnerable to a Denial of Service (DoS) due to inefficient HTTP body processing in the --listen mode due to inefficient HTTP body processing using repeated string concatenation, resulting in quadratic time complexity (O(n²)). A crafted POST request with many small segments can trigger excessive CPU usage during request handling.This allows a single malicious request to monopolize the single‑threaded HTTP server, blocking all other clients and resulting in denial of service.

This issue was fixed in version 0.73.1.

## References
- https://cert.pl/en/posts/2026/06/CVE-2026-53432
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53433.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53433
- https://github.com/junegunn/fzf/commit/7963a2c6586c0b9eaa89b8995de8f0e08cf8a4ce
- https://github.com/junegunn/fzf
