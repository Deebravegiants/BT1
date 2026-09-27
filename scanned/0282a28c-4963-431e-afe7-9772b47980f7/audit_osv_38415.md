# [C] Vvveb < 1.0.8.1 Code Injection via Installation Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-39918
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-39918
Type: osv

## Details
Vvveb prior to 1.0.8.1 contains a code injection vulnerability in the installation endpoint where the subdir POST parameter is written unsanitized into the env.php configuration file without escaping or validation. Attackers can inject arbitrary PHP code by breaking out of the string context in the define statement to achieve unauthenticated remote code execution as the web server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39918.json
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-39918
- https://www.vulncheck.com/advisories/vvveb-code-injection-via-installation-endpoint
- https://github.com/givanz/Vvveb/commit/5162c1639130bd080ab63c7d856788cd59d6b3b7
- https://github.com/givanz/Vvveb
