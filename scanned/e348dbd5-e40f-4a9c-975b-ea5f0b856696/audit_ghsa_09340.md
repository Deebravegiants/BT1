# [H] protobuf.js is Vulnerable to OS Command Injection in the CLI

## Summary
Severity: High
Advisory: GHSA-f84p-cvgm-xgjj
CVE: CVE-2026-42290
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-f84p-cvgm-xgjj
Type: github-advisory

## Affected
- npm: `protobufjs-cli` — affected >=0 <1.2.1
- npm: `protobufjs-cli` — affected >=2.0.0 <2.0.2

## Details
## Summary

`pbts` invoked JSDoc by building a shell command string from input file paths and executing it through `child_process.exec`. File paths containing shell metacharacters could therefore be interpreted by the shell instead of being passed to JSDoc as plain arguments.

## Impact

An attacker who can control file names or paths passed to `pbts` may be able to execute arbitrary shell commands with the privileges of the process running `pbts`.

This affects the protobufjs CLI tooling path. The protobufjs runtime APIs for encoding, decoding, parsing, and loading protobuf messages are not directly affected by this issue.

## Preconditions

- The application or user must invoke `pbts` on file paths influenced by an attacker.
- The attacker must be able to supply or create a path containing shell-significant characters.
- The vulnerable `pbts` version must execute the generated JSDoc command through a shell.

## Workarounds

Do not run affected versions of `pbts` on attacker-controlled file names or paths. If this cannot be avoided, sanitize or rename input files before invoking `pbts`, or run the CLI in an isolated environment with minimal privileges.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-f84p-cvgm-xgjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42290
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-cli-v1.2.1
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-cli-v2.0.2
