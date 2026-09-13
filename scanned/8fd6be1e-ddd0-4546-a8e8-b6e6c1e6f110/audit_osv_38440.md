# [C] parseusbs < 1.9 Command Injection via Volume Path Argument

## Summary
Severity: Critical
Advisory: CVE-2026-40030
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-40030
Type: osv

## Details
parseusbs before 1.9 contains an OS command injection vulnerability where the volume listing path argument (-v flag) is passed unsanitized into an os.popen() shell command with ls, allowing arbitrary command injection via crafted volume path arguments containing shell metacharacters. An attacker can provide a crafted volume path via the -v flag that injects arbitrary commands during volume content enumeration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40030.json
- https://mobasi.ai/sentinel
- https://nvd.nist.gov/vuln/detail/CVE-2026-40030
- https://www.vulncheck.com/advisories/parseusbs-command-injection-via-volume-path-argument
- https://github.com/khyrenz/parseusbs/pull/10
- https://github.com/khyrenz/parseusbs/commit/99f05996494e7e41ea0c7e13145ba20eb793e46b
