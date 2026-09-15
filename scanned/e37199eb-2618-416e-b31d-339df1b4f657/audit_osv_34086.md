# [H] Pearcleaner's unauthenticated access to privileged XPC helper allows root command execution

## Summary
Severity: High
Advisory: CVE-2025-54595
Aliases: GHSA-gr2j-65fh-8pvc
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-01
Source: https://osv.dev/vulnerability/CVE-2025-54595
Type: osv

## Details
Pearcleaner is a free, source-available and fair-code licensed mac app cleaner. The PearcleanerHelper is a privileged helper tool bundled with the Pearcleaner application. It is registered and activated only after the user approves a system prompt to allow privileged operations. Upon approval, the helper is configured as a LaunchDaemon and runs with root privileges. In versions 4.4.0 through 4.5.1, the helper registers an XPC service (com.alienator88.Pearcleaner.PearcleanerHelper) and accepts unauthenticated connections from any local process. It exposes a method that executes arbitrary shell commands. This allows any local unprivileged user to escalate privileges to root once the helper is approved and active. This issue is fixed in version 4.5.2.

## References
- https://github.com/alienator88/Pearcleaner/releases/tag/4.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54595.json
- https://github.com/alienator88/Pearcleaner/security/advisories/GHSA-gr2j-65fh-8pvc
- https://nvd.nist.gov/vuln/detail/CVE-2025-54595
- https://github.com/alienator88/Pearcleaner/issues/278
- https://github.com/alienator88/Pearcleaner/commit/69afadfa95791cb998118ca35c227007b230b984
