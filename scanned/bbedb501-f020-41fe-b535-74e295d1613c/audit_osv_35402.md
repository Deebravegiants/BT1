# [H] picklescan - Arbitrary Code Execution via Undetected asyncio.unix_events._UnixSubprocessTransport._start

## Summary
Severity: High
Advisory: CVE-2025-71364
Aliases: GHSA-q77w-mwjj-7mqx
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71364
Type: osv

## Details
picklescan before 0.0.30 fails to detect the asyncio.unix_events._UnixSubprocessTransport._start function in pickle reduce methods, allowing remote code execution. Attackers can craft malicious pickle files embedding this built-in function that evade detection but execute arbitrary commands when loaded.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71364.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-q77w-mwjj-7mqx
- https://nvd.nist.gov/vuln/detail/CVE-2025-71364
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-undetected-asyncio-unix-events-unixsubprocesstransport-start
