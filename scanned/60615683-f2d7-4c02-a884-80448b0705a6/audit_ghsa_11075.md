# [H] Docker CLI Plugins: Uncontrolled Search Path Element Leads to Local Privilege Escalation on Windows

## Summary
Severity: High
Advisory: GHSA-p436-gjf2-799p
CVE: CVE-2025-15558
CWE: CWE-427
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-p436-gjf2-799p
Type: github-advisory

## Affected
- Go: `github.com/docker/cli` — affected >=19.03.0 <29.2.0

## Details
This issue affects Docker CLI through 29.1.5

### Impact

Docker CLI for Windows searches for plugin binaries in `C:\ProgramData\Docker\cli-plugins`, a directory that does not exist by default. A low-privileged attacker can create this directory and place malicious CLI plugin binaries (docker-compose.exe, docker-buildx.exe, etc.) that are executed when a victim user opens Docker Desktop or invokes Docker CLI plugin features, and allow privilege-escalation if the `docker` CLI is executed as a privileged user.

This issue affects Docker CLI through v29.1.5 (fixed in v29.2.0). It impacts Windows binaries acting as a CLI plugin manager via the [`github.com/docker/cli/cli-plugins/manager`](https://pkg.go.dev/github.com/docker/cli@v29.1.5+incompatible/cli-plugins/manager) package, which is consumed by downstream projects such as Docker Compose.

Docker Compose became affected starting in v2.31.0, when it incorporated the relevant CLI plugin manager code (see https://github.com/docker/compose/pull/12300), and is fixed in v5.1.0.

This issue does not impact non-Windows binaries or projects that do not use the plugin manager code.

### Patches

Fixed version starts with 29.2.0

This issue was fixed in https://github.com/docker/cli/commit/13759330b1f7e7cb0d67047ea42c5482548ba7fa (https://github.com/docker/cli/pull/6713), which removed `%PROGRAMDATA%\Docker\cli-plugins` from the list of paths used for plugin-discovery on Windows.

### Workarounds

None

### Resources

- Pull request: "cli-plugins/manager: remove legacy system-wide cli-plugin path" (https://github.com/docker/cli/pull/6713)
- Patch: https://github.com/docker/cli/commit/13759330b1f7e7cb0d67047ea42c5482548ba7fa.patch

### Credits

Nitesh Surana (niteshsurana.com) of Trend Research of TrendAI

## References
- https://github.com/docker/cli/security/advisories/GHSA-p436-gjf2-799p
- https://nvd.nist.gov/vuln/detail/CVE-2025-15558
- https://github.com/docker/cli/pull/6713
- https://github.com/docker/compose/pull/12300
- https://github.com/docker/cli/commit/13759330b1f7e7cb0d67047ea42c5482548ba7fa
- https://docs.docker.com/desktop/release-notes
- https://github.com/docker/cli
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-28304
