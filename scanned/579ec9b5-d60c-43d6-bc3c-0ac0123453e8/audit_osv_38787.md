# [C] Remote Code Execution in Ollama via Update Mechanism

## Summary
Severity: Critical
Advisory: CVE-2026-42249
CVSS: 9.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-42249
Type: osv

## Details
Ollama for Windows contains a Remote Code Execution vulnerability in its update mechanism due to improper handling of attacker‑controlled HTTP response headers. When downloading updates, the application constructs local file paths using values derived from HTTP headers without validation. These values are passed directly to filepath.Join, allowing path traversal sequences (../) to be resolved and enabling files to be written outside the intended update staging directory.
An attacker who can influence update responses can exploit this flaw to write arbitrary executables to attacker‑chosen locations accessible to the current user, including the Windows Startup directory. This allows execution of arbitrary executables.

Critically, when chained with CVE‑2026‑42248 (Missing Signature Verification for Updates), an attacker can deliver malicious payloads that are written to sensitive locations and executed automatically. Because Ollama for Windows performs silent automatic updates and executes staged binaries without user interaction, this results in automatic and persistent code execution without user awareness.

Maintainers of this project were notified early about this vulnerability, but didn't respond with the details of vulnerability or vulnerable version range. Versions from 0.12.10 to 0.17.5 were tested and confirmed as vulnerable, other versions were not tested but might also be vulnerable.

## References
- https://ollama.com/
- https://cert.pl/en/posts/2026/04/CVE-2026-42248/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42249.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42249
- https://github.com/ollama/ollama
