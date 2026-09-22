# [H] Super Productivity: Arbitrary OS Command Execution via IPC EXEC Handler with Persistent Whitelist

## Summary
Severity: High
Advisory: CVE-2026-71551
Aliases: GHSA-256q-p9ff-jv8q
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-71551
Type: osv

## Details
Super Productivity is an advanced todo list app with integrated timeboxing and time tracking capabilities. Prior to 18.13.0, the EXEC IPC handler in electron/ipc-handlers/exec.ts accepts a command string from the renderer through the IPC.EXEC channel and executes it with child_process.exec(). The electron/preload.ts bridge exposes window.ea.exec() to renderer code, including community plugins executed with new Function(), without requiring nodeExecution permission. A confirmation dialog protects only the first execution, its persistence checkbox is selected by default, and approved commands are stored in the ALLOWED_COMMANDS value in simpleSettings for silent later execution with the desktop account's privileges. This issue is fixed in version 18.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71551.json
- https://github.com/super-productivity/super-productivity/security/advisories/GHSA-256q-p9ff-jv8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-71551
- https://github.com/super-productivity/super-productivity/commit/97e97042cde2e33524c9ad50dd46312c56be0072
- https://github.com/super-productivity/super-productivity/pull/8669
