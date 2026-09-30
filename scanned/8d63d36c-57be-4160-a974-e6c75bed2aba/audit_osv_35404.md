# [H] picklescan - Arbitrary Code Execution via Undetected doctest.debug_script

## Summary
Severity: High
Advisory: CVE-2025-71368
Aliases: GHSA-fqq6-7vqf-w3fg
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2025-71368
Type: osv

## Details
picklescan before 0.0.30 fails to detect the doctest.debug_script function when analyzing pickle files, allowing attackers to execute arbitrary code. Remote attackers can craft malicious pickle files embedding doctest.debug_script calls that bypass picklescan detection and execute arbitrary commands upon pickle.load invocation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71368.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-fqq6-7vqf-w3fg
- https://nvd.nist.gov/vuln/detail/CVE-2025-71368
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-undetected-doctest-debug-script
