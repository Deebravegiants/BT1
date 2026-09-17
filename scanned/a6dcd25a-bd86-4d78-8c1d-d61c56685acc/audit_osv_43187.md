# [C] goose: Arbitrary command execution in goose CLI via `goose review` via git core.fsmonitor

## Summary
Severity: Critical
Advisory: CVE-2026-72718
Aliases: GHSA-r5pp-p5r8-466r
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72718
Type: osv

## Details
goose is general-purpose AI agent that runs on your machine. Prior to 1.44.0, the `goose review` command runs the system `git` executable to gather the diff for review without stripping attacker-controlled Git configuration. A malicious repository whose `.git/config` sets [`core] fsmonitor = <command>` causes Git to execute that command on the host during the index refresh performed by `git diff HEAD`. The command runs before goose contacts a model and without a submitted prompt, model call, tool approval, or trust prompt. The context-gathering Git process is not sandboxed and is outside goose's tool-permission model. Arbitrary commands run with the privileges and environment of the user running goose, allowing file access or modification and exfiltration of environment secrets and provider API keys. The vulnerable Git invocations are built by git_command() in crates/goose-cli/src/commands/review/handler.rs and are used by touched_files() and collect_diff() for `git diff --name-only HEAD` and `git diff HEAD`. This issue is fixed in version 1.44.0.

## References
- https://github.com/aaif-goose/goose/releases/tag/v1.44.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72718.json
- https://github.com/aaif-goose/goose/security/advisories/GHSA-r5pp-p5r8-466r
- https://nvd.nist.gov/vuln/detail/CVE-2026-72718
- https://github.com/aaif-goose/goose/commit/f8b5b7ba1fe6d006ccf6942f6b85a1bae985a2de
