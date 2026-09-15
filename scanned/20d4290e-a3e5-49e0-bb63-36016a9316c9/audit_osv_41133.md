# [C] better-npm-audit OS Command Injection via registry flag

## Summary
Severity: Critical
Advisory: CVE-2026-57998
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-57998
Type: osv

## Details
better-npm-audit through 3.11.0, and the 4.0.0-rc.2 prerelease, builds its npm audit command by interpolating the user-supplied --registry option into a command string in src/handlers/handleInput.ts without validation or quoting, then passes that string to child_process.exec() in index.ts, which spawns a shell. A registry value containing shell metacharacters such as a semicolon, pipe, or command substitution executes arbitrary operating system commands with the privileges of the process running the audit.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57998.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57998
- https://www.vulncheck.com/advisories/better-npm-audit-os-command-injection-via-registry-flag
- https://github.com/jeemok/better-npm-audit/issues/119
- https://github.com/jeemok/better-npm-audit/pull/120
- https://github.com/jeemok/better-npm-audit
- https://github.com/jeemok/better-npm-audit/blob/fd99a0f41ff4342b8a0a6fdbe5a17261de3d0544/index.ts#L34
- https://github.com/jeemok/better-npm-audit/blob/fd99a0f41ff4342b8a0a6fdbe5a17261de3d0544/src/handlers/handleInput.ts#L30-L37
