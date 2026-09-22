# [H] picklescan - Remote Code Execution via Undetected idlelib.calltip.Calltip.fetch_tip

## Summary
Severity: High
Advisory: CVE-2025-71361
Aliases: GHSA-8r4j-24qv-fmq9, PYSEC-2026-1786
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2025-71361
Type: osv

## Details
picklescan before 0.0.29 fails to detect malicious idlelib.calltip.Calltip.fetch_tip calls in pickle files, allowing remote code execution. Attackers can embed undetected payloads in pickle files that execute arbitrary code when loaded via pickle.load().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71361.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-8r4j-24qv-fmq9
- https://nvd.nist.gov/vuln/detail/CVE-2025-71361
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-undetected-idlelib-calltip-calltip-fetch-tip
