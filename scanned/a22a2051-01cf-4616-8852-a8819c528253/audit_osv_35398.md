# [H] picklescan - Remote Code Execution via idlelib.autocomplete.AutoComplete.get_entity

## Summary
Severity: High
Advisory: CVE-2025-71358
Aliases: GHSA-6w4w-5w54-rjvr, PYSEC-2026-1784
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2025-71358
Type: osv

## Details
picklescan before 0.0.29 fails to detect malicious pickle files that exploit idlelib.autocomplete.AutoComplete.get_entity function in reduce methods. Attackers can embed undetected code in pickle files that executes arbitrary commands when loaded by victims using pickle.load().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71358.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-6w4w-5w54-rjvr
- https://nvd.nist.gov/vuln/detail/CVE-2025-71358
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-idlelib-autocomplete-autocomplete-get-entity
