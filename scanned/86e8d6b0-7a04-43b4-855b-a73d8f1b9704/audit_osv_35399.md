# [H] picklescan - Unsafe Deserialization via lib2to3.pgen2.grammar.Grammar.loads

## Summary
Severity: High
Advisory: CVE-2025-71359
Aliases: GHSA-f54q-57x4-jg88
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71359
Type: osv

## Details
picklescan before 0.0.29 fails to detect malicious pickle payloads that utilize lib2to3.pgen2.grammar.Grammar.loads in the reduce method, allowing remote code execution. Attackers can craft pickle files embedding dangerous code that evades picklescan detection and executes during pickle.load() deserialization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71359.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-f54q-57x4-jg88
- https://nvd.nist.gov/vuln/detail/CVE-2025-71359
- https://www.vulncheck.com/advisories/picklescan-unsafe-deserialization-via-lib2to3-pgen2-grammar-grammar-loads
