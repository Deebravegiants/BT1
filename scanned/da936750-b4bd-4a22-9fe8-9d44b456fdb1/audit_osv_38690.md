# [C] UAC < 3.3.0 Command Injection via User Substitution in parse_artifact.sh

## Summary
Severity: Critical
Advisory: CVE-2026-41451
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-41451
Type: osv

## Details
UAC (Unix-like Artifacts Collector) versions prior to 3.3.0 contain a command injection vulnerability in the user substitution logic within parse_artifact.sh where usernames and home directories from /etc/passwd are substituted directly into command strings without escaping before execution via eval. Attackers can inject shell metacharacters such as command substitution syntax or semicolons through crafted usernames or home directory paths in /etc/passwd entries to execute arbitrary commands on the analyst's host system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41451.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41451
- https://www.vulncheck.com/advisories/uac-command-injection-via-user-substitution-in-parse-artifact-sh
- https://github.com/tclahr/uac/pull/443
- https://github.com/tclahr/uac/commit/2cc367d8ead388f05abd3cfb8af537788a124e72
- https://github.com/tclahr/uac
