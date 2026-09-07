# [M] @apostrophecms/cli: Command Injection in apos create via Unsanitized Password Input

## Summary
Severity: Medium
Advisory: GHSA-hcwq-x9fw-8cfq
CVE: CVE-2026-42853
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-hcwq-x9fw-8cfq
Type: github-advisory

## Affected
- npm: `@apostrophecms/cli` — affected >=0

## Details
Summary

The @apostrophecms/cli package contains a command injection vulnerability in the apos create command.
User-supplied input from the password prompt is embedded directly into a shell command without proper sanitization or escaping.
This allows execution of arbitrary commands on the host system.

━━━━━━━━━━━━━━━━━━━━━━

Details

Vulnerable file: lib/commands/create.js
Location: Line 186

The CLI collects a password using an interactive prompt and passes it directly into a shell command.

Vulnerable code:

const response = await prompts({
type: 'password',
name: 'pw',
message: '🔏 Please enter a password:'
});

exec(echo "${response.pw}" | ${createUserCommand});

The value of response.pw is not validated, sanitized, or escaped before being used in exec().

This allows shell metacharacters such as ;, &&, and $() to break out of the intended command and execute arbitrary commands.

━━━━━━━━━━━━━━━━━━━━━━

Steps to Reproduce

1) Install the CLI
      npm install -g @apostrophecms/cli
2) Create a new project
      mkdir testproject && cd testproject
      apos create mysite
3)When prompted for the admin password, enter
      "; id > /tmp/apos_rce_proof.txt; echo "
4)Verify command execution
        cat /tmp/apos_rce_proof.txt

━━━━━━━━━━━━━━━━━━━━━━

Proof of Concept Output

uid=1000(vboxuser) gid=1000(vboxuser) groups=1000(vboxuser),27(sudo),984(docker)

This confirms arbitrary command execution with the privileges of the user running the CLI.

━━━━━━━━━━━━━━━━━━━━━━

Impact

Arbitrary command execution on the developer’s machine
Execution occurs with the privileges of the user running the CLI

This can lead to:

File modification or deletion
Credential exposure
System compromise depending on user privileges

An attacker can exploit this by influencing the password input (for example, through social engineering, malicious documentation, or compromised automation scripts).

The proof-of-concept shows execution under a user belonging to privileged groups such as sudo and docker, which may allow further privilege escalation depending on system configuration.

━━━━━━━━━━━━━━━━━━━━━━

Suggested Fix

Avoid using exec() with user-controlled input.

Use execFile() instead:

const { execFileSync } = require('child_process');

execFileSync('node', [appJsPath, userTask, 'admin', 'admin'], {
input: response.pw + '\n'
});

━━━━━━━━━━━━━━━━━━━━━━

Affected Version

All current versions of @apostrophecms/cli

━━━━━━━━━━━━━━━━━━━━━━

Tested On

Ubuntu 22.04
Node.js v18.19.1

━━━━━━━━━━━━━━━━━━━━━━

CWE

CWE-78 — Improper Neutralization of Special Elements used in an OS Command

━━━━━━━━━━━━━━━━━━━━━━

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-hcwq-x9fw-8cfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42853
- https://github.com/apostrophecms/apostrophe
