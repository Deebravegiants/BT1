# [M] @cyclonedx/cdxgen: Maven project scanning may allow shell command injection through repository-controlled module paths

## Summary
Severity: Medium
Advisory: GHSA-5vwr-qchf-q4pf
CWE: CWE-78, CWE-88
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-5vwr-qchf-q4pf
Type: github-advisory

## Affected
- npm: `@cyclonedx/cdxgen` — affected >=0 <12.4.3

## Details
## Summary

A command injection vulnerability existed in the Maven scanning flow of cdxgen before version 12.4.3.

When cdxgen scanned an attacker-controlled Maven project, repository-controlled paths could be used in the Maven command construction. In affected versions, some Maven invocations were executed with `shell: true`. A directory name containing shell metacharacters could therefore be interpreted by the shell instead of being treated only as a filesystem path.

This could allow an attacker who controls a scanned repository to execute commands in the cdxgen process context.

The issue affected both the CLI and server mode. The issue is patched in `12.4.3`.

## Affected asset

- Project: cdxgen
- Tested version: 12.4.1
- Mode tested: server mode
- Endpoint: `POST /sbom`
- Scanner path: Java / Maven project scanning

## Patch

Version 12.4.3 includes hardening for this issue with PR #4059 

The patch adds multiple mitigations:

- Maven command invocations no longer use unconditional shell execution on POSIX platforms.
- Bazel command invocation was similarly changed away from unconditional shell execution.
- Windows compatibility is preserved using `shell: isWin` where needed.
- `safeSpawnSync` now blocks `shell: true` invocations when the command or direct argument values contain shell metacharacters.
- cdxgen does not validate or sanitise every nested directory. The threat model is updated to clarify mitigation scope.

## Workarounds

The recommended remediation is to upgrade to 12.4.3 or later.

If immediate upgrade is not possible:

- Do not run cdxgen server mode on untrusted networks.
- Do not expose POST /sbom to unauthenticated or untrusted clients.
- Avoid scanning untrusted Java/Maven repositories.
- Run cdxgen inside a locked-down container or sandbox.
- Remove sensitive environment variables from the cdxgen process environment.
- Use least-privilege filesystem mounts.
- Restrict outbound network access where possible.

Use cdxgen secure/dry-run modes where suitable to inspect planned operations before performing scans.
Configure host and command allowlists where applicable, such as:

- CDXGEN_SERVER_ALLOWED_HOSTS
- CDXGEN_GIT_ALLOWED_HOSTS
- CDXGEN_ALLOWED_COMMANDS
- CDXGEN_SECURE_MODE=true

These mitigations reduce exposure but do not fully address the vulnerable command construction in affected versions.

## Threat model clarification

The mitigation added in 12.4.3 applies to the cdxgen process boundary. Specifically, cdxgen now hardens command, option, and path values that cdxgen itself passes to external processes through safeSpawnSync.

This does not mean cdxgen sanitizes every nested path, module name, generated path, or project-controlled value that an external build tool later discovers and interprets inside its own process. Once cdxgen safely invokes Maven, Gradle, Bazel, SBT, or another build tool, that tool’s internal behavior remains a separate trust boundary.

### In scope for this fix:

- command and argument values passed directly by cdxgen to child processes;
- cdxgen’s own use of shell: true;
- Maven/Bazel command invocation paths controlled by cdxgen.

### Out of scope for this specific mitigation:
- arbitrary nested paths later discovered by Maven itself;
- Maven plugin behavior;
- Maven lifecycle hooks;
- build-tool-specific interpretation of project files after cdxgen has launched the tool.

This residual risk is documented in the cdxgen threat model and is why untrusted project scans should still be run in sandboxed, least-privileged environments.

## Detection

Possible indicators of exploitation or probing include:

- Maven module directories containing shell metacharacters such as:

```
;
&
|
<
>
$
backticks
newlines
```

- Logs showing settings.xml or pom.xml discovered in suspicious paths.
- Unexpected files created outside the scanned repository during a Java/Maven scan.
- Unexpected child process behavior during cdxgen server scans.
- cdxgen server receiving POST /sbom requests for attacker-controlled Git URLs.

Example suspicious path pattern:

```
evil;cd${IFS}..;cd${IFS}..;printf${IFS}...>...;#
```

## Credits

Reported-By: @aleff-github 

## Resources

- Patch PR - https://github.com/cdxgen/cdxgen/pull/4059

## References
- https://github.com/cdxgen/cdxgen/security/advisories/GHSA-5vwr-qchf-q4pf
- https://github.com/cdxgen/cdxgen/pull/4059
- https://github.com/cdxgen/cdxgen
