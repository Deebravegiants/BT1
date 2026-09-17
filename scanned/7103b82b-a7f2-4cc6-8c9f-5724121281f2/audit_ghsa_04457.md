# [H] @cyclonedx/cyclonedx-npm: Shell Injection via Unsanitized --workspace Argument

## Summary
Severity: High
Advisory: GHSA-v75r-vx73-82pj
CVE: CVE-2026-55849
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-v75r-vx73-82pj
Type: github-advisory

## Affected
- npm: `@cyclonedx/cyclonedx-npm` — affected >=2.1.0 <5.0.0

## Details
## Summary
A command injection vulnerability exists in `@cyclonedx/cyclonedx-npm` when the CLI is invoked with the `--workspace <value>` option while the environment variable `npm_execpath` is unset or empty.  
User‑supplied `--workspace` values are passed to a subshell without proper sanitization, enabling attackers to inject arbitrary OS commands.  
This issue corresponds to **CWE‑78**: Improper Neutralization of Special Elements used in an OS Command.

The vulnerability was fixed in version [5.0.0][v5.0.0].

## Vulnerability Details

When `cyclonedx-npm` is executed with the `--workspace` option, the provided argument is incorporated into an internal shell command.  
If the environment variable `npm_execpath` is set, the tool uses the npm executable directly and no injection occurs.  
However, when `npm_execpath` is unset or empty, the tool falls back to spawning a subshell and interpolating the `--workspace` value directly into the command string without proper escaping or neutralization.

As a result, specially crafted workspace names can break out of the intended command context and execute arbitrary commands with the privileges of the invoking user.

## Impact

An attacker who can influence the value passed to `--workspace` can execute arbitrary OS commands.  
This may lead to:

* Arbitrary command execution
* Data exfiltration
* Local privilege escalation (depending on how the tool is used)
* Modification or destruction of files accessible to the user running the CLI

The vulnerability affects only scenarios where:
* The user invokes `cyclonedx-npm` with `--workspace <value>`, and
* The environment variable `npm_execpath` is unset or empty

## Exploitation Conditions (High‑Level)

Exploitation requires the attacker to supply or influence the `--workspace` value passed to the CLI.  
If the tool falls back to its subshell execution path, specially crafted workspace identifiers can cause unintended command execution.  
No exploit code is included here to avoid providing weaponizable examples.

## Root Cause

The CLI constructs a shell command using untrusted input from the `--workspace` option.  
Because the fallback code path does not sanitize or escape the workspace value, special shell metacharacters (e.g., `;`, `&&`, `|`) are interpreted by the shell, enabling command injection.

This behavior matches **CWE‑78**.

## Fix

The vulnerability was resolved in [PR #1476], which ensures that workspace values are handled safely and are no longer passed to a subshell in an unsafe manner.

The fix is included in `@cyclonedx/cyclonedx-npm` version [5.0.0][v5.0.0].

## Remediation

* Upgrade to version [5.0.0][v5.0.0] or later, which contains the complete fix.
* As a temporary mitigation for older versions, ensure that the environment variable `npm_execpath` is set before invoking the tool.
* Avoid passing untrusted or user‑controlled values to the `--workspace` option.

[v5.0.0]: https://github.com/CycloneDX/cyclonedx-node-npm/releases/tag/v5.0.0
[PR #1476]: https://github.com/CycloneDX/cyclonedx-node-npm/pull/1476

## References
- https://github.com/CycloneDX/cyclonedx-node-npm/security/advisories/GHSA-v75r-vx73-82pj
- https://github.com/CycloneDX/cyclonedx-node-npm/pull/1476
- https://github.com/CycloneDX/cyclonedx-node-npm
- https://github.com/CycloneDX/cyclonedx-node-npm/releases/tag/v5.0.0
