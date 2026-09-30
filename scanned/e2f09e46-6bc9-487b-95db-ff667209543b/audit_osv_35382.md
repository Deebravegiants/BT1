# [H] picklescan - Remote Code Execution via idlelib.pyshell.ModifiedInterpreter.runcode

## Summary
Severity: High
Advisory: CVE-2025-71340
Aliases: GHSA-3gf5-cxq9-w223
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2025-71340
Type: osv

## Details
picklescan through 0.0.26 fails to detect malicious pickle files that invoke idlelib.pyshell.ModifiedInterpreter.runcode in __reduce__ methods. Attackers can embed undetected code in pickle files that executes arbitrary commands when the file is loaded via pickle.load(), enabling supply chain attacks on PyTorch models and saved Python objects. This is fixed in version 0.0.30.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71340.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-3gf5-cxq9-w223
- https://nvd.nist.gov/vuln/detail/CVE-2025-71340
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-idlelib-pyshell-modifiedinterpreter-runcode
