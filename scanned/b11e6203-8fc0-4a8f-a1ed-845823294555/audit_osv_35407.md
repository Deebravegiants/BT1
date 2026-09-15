# [H] picklescan - Arbitrary Code Execution via Undetected idlelib.autocomplete.AutoComplete.fetch_completions

## Summary
Severity: High
Advisory: CVE-2025-71376
Aliases: GHSA-7cq8-mj8x-j263
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2025-71376
Type: osv

## Details
picklescan before 0.0.29 fails to detect malicious pickle files using idlelib.autocomplete.AutoComplete.fetch_completions in reduce methods. Attackers can embed undetected code in pickle files that executes arbitrary commands when loaded by victims.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71376.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-7cq8-mj8x-j263
- https://nvd.nist.gov/vuln/detail/CVE-2025-71376
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-undetected-idlelib-autocomplete-autocomplete-fetch-completions
