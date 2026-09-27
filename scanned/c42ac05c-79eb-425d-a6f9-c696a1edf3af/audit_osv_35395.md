# [H] Picklescan - Arbitrary Code Execution via Unsafe Numpy Function Detection Bypass

## Summary
Severity: High
Advisory: CVE-2025-71355
Aliases: GHSA-fj43-3qmq-673f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2025-71355
Type: osv

## Details
Picklescan before 0.0.25 fails to detect unsafe global functions in the Numpy library, allowing attackers to bypass static analysis and execute arbitrary code during deserialization. Attackers can craft malicious pickle files using numpy.testing._private.utils.runstring within the reduce method to import dangerous libraries like os and execute arbitrary OS commands when the pickle file is loaded.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71355.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-fj43-3qmq-673f
- https://nvd.nist.gov/vuln/detail/CVE-2025-71355
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-unsafe-numpy-function-detection-bypass
