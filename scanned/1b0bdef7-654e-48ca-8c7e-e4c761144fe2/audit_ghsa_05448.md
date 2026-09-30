# [M] Renovate vulnerable to arbitrary command injection via Gradle Wrapper and malicious `distributionUrl`

## Summary
Severity: Medium
Advisory: GHSA-pfq2-hh62-7m96
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-pfq2-hh62-7m96
Type: github-advisory

## Affected
- npm: `renovate` — affected >=32.124.0 <42.68.5

## Details
### Summary
Renovate can be tricked into executing shell code while updating the Gradle Wrapper. A malicious `distributionUrl` in `gradle/wrapper/gradle-wrapper.properties` can lead to command execution in the Renovate runtime.

### Details
When Renovate handles Gradle Wrapper artifacts, it may run a wrapper update command such as:
- `./gradlew :wrapper --gradle-distribution-url <value>`

In the observed behavior, Renovate executes this via a shell (e.g., `/bin/sh -c ...`).  
If `distributionUrl` contains shell command substitution syntax like `$(...)`, the shell evaluates it **before** Gradle validates/parses the URL.

After that, Gradle attempts to parse the URL as a URI and fails with `URISyntaxException`, but the shell substitution has already executed.

This is reproducible even when `allowScripts` is disabled (default is OFF), because this execution happens as part of Gradle Wrapper artifact handling rather than “repository install scripts”.

Prerequisites / attack conditions:
- The attacker must be able to get a malicious `gradle-wrapper.properties` into a repository that Renovate scans (e.g., direct write access, or a maintainer merges an attacker’s change/PR).
- Renovate must be configured to process Gradle Wrapper updates/artifacts for that repository (default behavior for the Gradle Wrapper manager).

### PoC
1. Create a repository with a Gradle Wrapper (`gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.jar`, and `gradle/wrapper/gradle-wrapper.properties`).
2. Set `distributionUrl` in `gradle-wrapper.properties` to include `$(...)`.
3. Run Renovate against the repository.
4. Observe that a file is created during Renovate’s wrapper update step **before** Gradle fails with `URISyntaxException`.

A [screen recording](https://drive.google.com/file/d/1nveSCgyz4pKPCZuelqDD_xGEO00DXr4P/view) is attached showing end-to-end reproduction. In the demo, the payload creates `/tmp/passwd_dump` containing `/etc/passwd`, demonstrating that file read/exfiltration is possible within the Renovate execution context.

### Impact
This allows arbitrary command execution in the Renovate runtime during Gradle Wrapper updates. Depending on deployment, this may expose credentials/tokens available to the bot and may allow an attacker to modify repositories or access internal resources reachable from the Renovate environment.

### Remediation

Upgrading to Renovate [42.68.5](https://github.com/renovatebot/renovate/releases/tag/42.68.5) (2025-12-31) fixes this issue, and closes out other risks of shell evaluation for commands run by Renovate.

If using the `composer`, `yarn` (v1) or `flux` managers, please upgrade to [42.74.5](https://github.com/renovatebot/renovate/releases/tag/42.74.5) (2026-01-08), as there were follow-up fixes to keep these managers working.

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-pfq2-hh62-7m96
- https://github.com/renovatebot/renovate
- https://github.com/renovatebot/renovate/releases/tag/42.68.5
