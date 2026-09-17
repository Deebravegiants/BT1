# [H] picklescan - Undetected Remote Code Execution via idlelib.run.Executive.runcode

## Summary
Severity: High
Advisory: CVE-2025-71342
Aliases: GHSA-m869-42cg-3xwr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71342
Type: osv

## Details
picklescan before 0.0.30 fails to detect malicious pickle files using idlelib.run.Executive.runcode in reduce methods. Attackers can embed undetected code in pickle files that executes during pickle.load, enabling remote code execution in PyTorch models and supply chain attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71342.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-m869-42cg-3xwr
- https://nvd.nist.gov/vuln/detail/CVE-2025-71342
- https://www.vulncheck.com/advisories/picklescan-undetected-remote-code-execution-via-idlelib-run-executive-runcode
