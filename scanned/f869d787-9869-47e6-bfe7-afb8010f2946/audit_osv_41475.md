# [C] PraisonAI before 4.6.78 Code Injection via f-string

## Summary
Severity: Critical
Advisory: CVE-2026-61444
Aliases: GHSA-g6j7-pffp-8whg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-61444
Type: osv

## Details
PraisonAI versions before 4.6.78 contain a code injection vulnerability in deploy/api.py where the agents_file parameter is directly interpolated into an f-string without sanitization. Attackers can inject arbitrary Python code that executes when the generated server code runs via subprocess.Popen().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61444.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-g6j7-pffp-8whg
- https://nvd.nist.gov/vuln/detail/CVE-2026-61444
- https://www.vulncheck.com/advisories/praisonai-before-code-injection-via-f-string
