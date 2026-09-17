# [C] UAC < 3.3.0 Command Injection via command_collector.sh

## Summary
Severity: Critical
Advisory: CVE-2026-41450
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-41450
Type: osv

## Details
UAC (Unix-like Artifacts Collector) versions prior to 3.3.0 contain a command injection vulnerability in the _command_collector function where foreach command output lines are substituted directly into command strings via sed without proper escaping before being evaluated with eval. Attackers can exploit this by crafting malicious filenames or artifact definitions containing shell metacharacters such as command substitution syntax or semicolons to execute arbitrary commands on the analyst's host system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41450
- https://www.vulncheck.com/advisories/uac-command-injection-via-command-collector-sh
- https://github.com/tclahr/uac/pull/443
- https://github.com/tclahr/uac/commit/2cc367d8ead388f05abd3cfb8af537788a124e72
- https://github.com/tclahr/uac
