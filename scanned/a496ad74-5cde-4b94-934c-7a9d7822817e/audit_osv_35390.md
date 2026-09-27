# [H] picklescan - Undetected Remote Code Execution via torch.utils.collect_env.run

## Summary
Severity: High
Advisory: CVE-2025-71350
Aliases: GHSA-f745-w6jp-hpxx
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2025-71350
Type: osv

## Details
picklescan before 0.0.28 fails to detect malicious pickle files using torch.utils.collect_env.run function in reduce methods. Attackers can embed undetected code in pickle files that executes remote commands when loaded by victims.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71350.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-f745-w6jp-hpxx
- https://nvd.nist.gov/vuln/detail/CVE-2025-71350
- https://www.vulncheck.com/advisories/picklescan-undetected-remote-code-execution-via-torch-utils-collect-env-run
