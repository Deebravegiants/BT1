# [C] UAC < 3.3.0 Command Injection via run_command.sh

## Summary
Severity: Critical
Advisory: CVE-2026-41449
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-41449
Type: osv

## Details
UAC (Unix-like Artifacts Collector) versions prior to 3.3.0 contain a command injection vulnerability in the _run_command function that allows attackers to execute arbitrary commands by injecting shell metacharacters into untrusted data such as usernames, process names, or filenames. Attackers can exploit this vulnerability through crafted evidence inputs, mounted images with hostile filenames, or tampered artifact definitions to achieve remote code execution on the analyst's host when processing evidence.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41449.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41449
- https://www.vulncheck.com/advisories/uac-command-injection-via-run-command-sh
- https://github.com/tclahr/uac/pull/443
- https://github.com/tclahr/uac/commit/2cc367d8ead388f05abd3cfb8af537788a124e72
- https://github.com/tclahr/uac
