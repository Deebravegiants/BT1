# [H] ouroboros-ai Vulnerable to Remote Code Execution via Untrusted Project-Directory .env

## Summary
Severity: High
Advisory: GHSA-c4m7-2gwp-vw76
CVE: CVE-2026-47211
CWE: CWE-426
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-c4m7-2gwp-vw76
Type: github-advisory

## Affected
- PyPI: `ouroboros-ai` — affected >=0 <0.39.0

## Details
### Impact
A Remote Code Execution (RCE) vulnerability was discovered in Ouroboros. If a user clones a malicious repository and runs Ouroboros commands within that directory, it can lead to arbitrary code execution and potential system takeover.

The vulnerability (CWE-426: Untrusted Search Path & CWE-15: External Control of System Setting) stems from Ouroboros loading the `.env` file from the current working directory. Prior to the patch, execution-affecting environment variables such as `OUROBOROS_CLI_PATH`, `OPENCODE_CLI_PATH`, and other backend selectors were accepted directly from this local `.env`. An attacker could include a malicious script in the repository and point the CLI path variable to it (e.g., `OUROBOROS_CLI_PATH=./malicious_script.sh`). When the user executes a command like `ouroboros init` or any command that instantiates the adapter, the malicious script is executed instead of the intended CLI.

### Patches
The vulnerability has been patched in version 0.39.0 via PR #1078.
The fix establishes a strict trust boundary by applying a denylist to project-local `.env` loading. It blocks execution-affecting environment variables (such as runtime selectors and CLI path overrides) from being loaded from the project directory. Explicit constructor overrides and trusted user-owned home configurations (`~/.ouroboros/.env`) remain fully functional. 

Users are strongly advised to upgrade to version 0.39.0 or later.

### Workarounds
If upgrading is not immediately possible, users must carefully inspect any `.env` file inside cloned repositories before running Ouroboros commands to ensure it does not contain unexpected `OUROBOROS_*_CLI_PATH` or `OPENCODE_CLI_PATH` overrides.

### References
- GitHub PR: https://github.com/Q00/ouroboros/pull/1078

## References
- https://github.com/Q00/ouroboros/security/advisories/GHSA-c4m7-2gwp-vw76
- https://github.com/Q00/ouroboros/pull/1078
- https://github.com/Q00/ouroboros/commit/4e70b760b4eb157469b58645339ba831f6513d37
- https://github.com/Q00/ouroboros
