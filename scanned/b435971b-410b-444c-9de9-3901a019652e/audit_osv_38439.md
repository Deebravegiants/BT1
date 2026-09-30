# [C] parseusbs < 1.9 Command Injection via Crafted LNK Filename

## Summary
Severity: Critical
Advisory: CVE-2026-40029
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-40029
Type: osv

## Details
parseusbs before 1.9 contains an OS command injection vulnerability in parseUSBs.py where LNK file paths are passed unsanitized into an os.popen() shell command, allowing arbitrary command execution via crafted .lnk filenames containing shell metacharacters. An attacker can craft a .lnk filename with embedded shell metacharacters that execute arbitrary commands on the forensic examiner's machine during USB artifact parsing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40029.json
- https://mobasi.ai/sentinel
- https://nvd.nist.gov/vuln/detail/CVE-2026-40029
- https://www.vulncheck.com/advisories/parseusbs-command-injection-via-crafted-lnk-filename
- https://github.com/khyrenz/parseusbs/pull/10
- https://github.com/khyrenz/parseusbs/commit/99f05996494e7e41ea0c7e13145ba20eb793e46b
