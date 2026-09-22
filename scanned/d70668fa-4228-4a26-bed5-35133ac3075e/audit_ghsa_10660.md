# [H] OpenTelemetry eBPF Instrumentation: Privileged Java agent injection allows arbitrary host file overwrite via untrusted TMPDIR

## Summary
Severity: High
Advisory: GHSA-8gmg-3w2q-65f4
CVE: CVE-2026-41433
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-8gmg-3w2q-65f4
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0.4.0 <0.8.0

## Details
### Summary

A flaw in the Java agent injection path allows a local attacker controlling a Java workload to overwrite arbitrary host files when Java injection is enabled and OBI is running with elevated privileges. The injector trusted `TMPDIR` from the target process and used unsafe file creation semantics, enabling both filesystem boundary escape and symlink-based file clobbering.

### Remediation

Upgrade to https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.8.0.

### Details

The issue is in the Java agent staging logic in `pkg/internal/java/java_inject.go`.

The injector reads `TMPDIR` from the target process environment in `findTempDir(...)` and validates it with `dirOK(...)`. In the vulnerable implementation, `dirOK(...)` used `filepath.Join(root, dir)`, where `root` is `/proc/<pid>/root`. If `dir` is an absolute path, `filepath.Join` discards `root`, so values such as `/etc` or `/proc/1/root/etc` are resolved on the host instead of within the target process root.

That validated value is later reused in `copyAgent(...)` to build the destination path for the Java agent JAR. As a result, a malicious process can influence the privileged injector to write outside the intended `/proc/<pid>/root` boundary.

The file creation step further increases impact. The vulnerable code created the destination with `os.OpenFile(..., os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0o644)`. Because this does not use exclusive creation or symlink protections, an attacker can pre-create a symlink at the chosen destination, for example in a writable temp directory, and cause the injector to truncate or overwrite another file writable by the privileged OBI process.

Relevant code paths:

- `pkg/internal/java/java_inject.go`: `findTempDir(...)`
- `pkg/internal/java/java_inject.go`: `dirOK(...)`
- `pkg/internal/java/java_inject.go`: `copyAgent(...)`

In short, the vulnerability is caused by two issues acting together:

1. Untrusted `TMPDIR` from the target process can escape the intended target root.
2. The destination JAR is written with unsafe open semantics that allow clobbering via symlink or attacker-controlled destination selection.

### PoC

Prerequisites:

- OBI is running with elevated privileges on the host.
- Java injection is enabled.
- The attacker can run or control a Java process on the same host.

Reproduction outline for the path escape case:

1. Start a Java process with a controlled environment variable such as:
   - `TMPDIR=/etc`
   - or `TMPDIR=/proc/1/root/etc`
2. Ensure the process is discovered by OBI and selected for Java agent injection.
3. Wait for the injector to stage the agent JAR.
4. Observe that the injector attempts to write `obi-java-agent.jar` outside `/proc/<pid>/root`, under the attacker-controlled host path.

Reproduction outline for the symlink clobber case:

1. Start a Java process with `TMPDIR=/tmp` or another writable temp directory.
2. Before injection occurs, create a symlink at the expected destination:
   - `/tmp/obi-java-agent.jar -> /path/to/target/file`
3. Trigger Java agent injection for that process.
4. Observe that the privileged injector opens the symlink target with truncate semantics and overwrites the linked file contents.

Code evidence:

- `findTempDir(...)` reads `ie.FileInfo.Service.EnvVars["TMPDIR"]`
- `dirOK(...)` validates using `filepath.Join(root, dir)`
- `copyAgent(...)` writes the JAR into the selected temp directory
- the vulnerable write uses `os.OpenFile(..., os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0o644)`

### Impact

This is an arbitrary file overwrite / file clobber vulnerability in a privileged host component.

Affected users are deployments where:

- Java injection is enabled
- OBI runs with elevated privileges
- untrusted local workloads can run Java processes on the same host

An attacker who can control a local Java process may be able to overwrite host files writable by OBI, which can lead to:

- host integrity compromise
- service disruption or denial of service
- possible local privilege escalation depending on deployment details and overwritten targets

The issue is local rather than remote, but the impact is high because the vulnerable component operates with elevated privileges on the host.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-8gmg-3w2q-65f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41433
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.8.0
