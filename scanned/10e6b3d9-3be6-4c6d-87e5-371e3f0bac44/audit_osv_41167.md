# [M] Authenticated Remote Denial of Service via Unbounded zlib Decompression in massStoreRun

## Summary
Severity: Medium
Advisory: CVE-2026-58107
Aliases: GHSA-w7jw-x567-hqr4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P/S:N/AU:Y/R:A/RE:L)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-58107
Type: osv

## Details
CodeChecker's massStoreRun processing path performs one-shot decompression of attacker-controlled, Base64-encoded zlib data without enforcing a maximum decompressed size.



An authenticated user with permission to store analysis runs can submit a highly compressed payload that expands to a significantly larger byte sequence. Because the entire decompressed output is materialized in memory before being written to a temporary file, a sufficiently large payload may exhaust process or host memory and consume substantial disk space, resulting in denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58107.json
- https://github.com/Ericsson/codechecker/security/advisories/GHSA-w7jw-x567-hqr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-58107
