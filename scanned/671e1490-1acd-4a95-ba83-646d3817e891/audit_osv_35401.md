# [H] picklescan - Arbitrary Code Execution via Undetected cProfile.run in Pickle Deserialization

## Summary
Severity: High
Advisory: CVE-2025-71363
Aliases: GHSA-49gj-c84q-6qm9
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2025-71363
Type: osv

## Details
picklescan before 0.0.30 fails to detect cProfile.run function calls in pickle reduce methods, allowing attackers to execute arbitrary code. Remote attackers can craft malicious pickle files with cProfile.run payloads that bypass picklescan detection and achieve code execution upon deserialization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71363.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-49gj-c84q-6qm9
- https://nvd.nist.gov/vuln/detail/CVE-2025-71363
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-undetected-cprofile-run-in-pickle-deserialization
