# [H] picklescan - Arbitrary Code Execution via Undetected idlelib.pyshell.ModifiedInterpreter.runcommand

## Summary
Severity: High
Advisory: CVE-2025-71357
Aliases: GHSA-j343-8v2j-ff7w, PYSEC-2026-246
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2025-71357
Type: osv

## Details
picklescan before 0.0.30 fails to detect malicious pickle files using idlelib.pyshell.ModifiedInterpreter.runcommand in reduce methods. Attackers can embed undetected code in pickle files that executes remote commands when loaded by victims.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71357.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-j343-8v2j-ff7w
- https://nvd.nist.gov/vuln/detail/CVE-2025-71357
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-undetected-idlelib-pyshell-modifiedinterpreter-runcommand
