# [C] Missing Signature Verification for Updates in Ollama

## Summary
Severity: Critical
Advisory: CVE-2026-42248
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-42248
Type: osv

## Details
Ollama for Windows does not perform integrity or authenticity verification of downloaded update executables. Unlike other platforms, the Windows implementation of the update verification routine unconditionally returns success so no digital signature or trust validation is performed before staging or executing update payloads, enabling attacker‑supplied executables to be accepted and later executed by the application.

Critically, Ollama for Windows performs silent automatic updates, so the malicious payload may be installed automatically without user awareness.

Maintainers of this project were notified early about this vulnerability, but didn't respond with the details of vulnerability or vulnerable version range. Versions from 0.12.10 to 0.17.5 were tested and confirmed as vulnerable, other versions were not tested but might also be vulnerable.

## References
- https://ollama.com/
- https://cert.pl/en/posts/2026/04/CVE-2026-42248/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42248.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42248
- https://github.com/ollama/ollama
