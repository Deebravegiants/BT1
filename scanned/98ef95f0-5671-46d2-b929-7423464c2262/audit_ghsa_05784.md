# [H] PowSyBl Core has Command Injection in LocalCommandExecutor-s

## Summary
Severity: High
Advisory: GHSA-jqvf-j3ww-r8c7
CVE: CVE-2026-55673
CWE: CWE-78, CWE-88
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-jqvf-j3ww-r8c7
Type: github-advisory

## Affected
- Maven: `com.powsybl:powsybl-computation-local` — affected >=0 <7.2.2

## Details
### Impact

#### Description
Both `AbstractLocalCommandExecutor` OS-dependent implementations are subject to **CWE-78** (OS Command Injection), with a secondary **CWE-88** (Argument Injection) concern via environment variables.

The local command executor build command strings via concatenation and executes them (through `bash -c` for Unix, or `cmd /c` for Windows). Any string argument or environment variable value reaching this executor can break out of the intended command and execute arbitrary shell code as the JVM user.

The sink is reachable through public APIs that accept `List<String>` arguments without any documented indication that elements undergo shell interpretation.

Any caller — CLI, library integration, or embedding service — that forwards data from a less-trusted source into these APIs inherits the vulnerability.

#### Vulnerable elements
The vulnerable elements are:
- Public methods:
  - `UnixLocalCommandExecutor.execute(...)`
  - `WindowsLocalCommandExecutor.execute(...)`
  - `LocalComputationManager.execute(...)`
  - `ParallelLoadFlowActionSimulator.run(...)`
  - `ActionSimulatorTool.run(...)`
  - `AmplModelRunner.run(...)`
  - `AmplModelRunner.runAsync(...)`
- **itools** commands:
  - `action-simulator`, when the `task-count` option is defined
  - `security-analysis`, when the `external` option is defined
  -  `dynamic-security-analysis`


#### Characteristics

The vulnerability characteristics are the following:
- It allows **arbitrary shell command execution** as the JVM user (read, write, execute any file; spawn processes; exfiltrate data; etc.)
- There are **multiple independent injection vectors** within a single vulnerable call:
  - `args` elements (weakly escaped — bypassable via `$(...)`, backticks, escaped quotes)
  - Environment variable values (unescaped — bypassable via `;`, `\n`, or shell metacharacters)
- It is **silent** from the caller's perspective: the `List<String>` API gives no indication that shell interpretation occurs.
- It exposes **downstream projects:** any service embedding `powsybl-core` (REST front-ends, pypowsybl tooling, multi-tenant grid analysis platforms) that exposes contingency IDs or computation parameters to external input is exploitable without needing to touch powsybl's code directly.


#### Am I impacted?

You are vulnerable if you make direct calls to one of the vulnerable end-user methods or itools commands listed in the "Vulnerable elements" section, with user-provided parameters, without controlling them.


### Patches

`com.powsybl:powsybl-computation-local:7.2.2` and higher


### Workarounds

If you cannot update your `powsybl-computation-local` version, you can check the content of the user-provided arguments when calling the vulnerable methods, by forbidding (if possible) the following characters:
- On Unix/Linux systems:
  - `\`, `!`, `#`, `$`, `^`, `&`, `*`, `(`, `)`, `{`, `}`, `|`, `[`, `]`, `\`, `;`, `\`, `"`, `,`, `<`, `>`, `?`, ` `
- On Windows:
  - `%`, `!`, `"`, `\n`, `\r`, `^`

## References
- https://github.com/powsybl/powsybl-core/security/advisories/GHSA-jqvf-j3ww-r8c7
- https://github.com/powsybl/powsybl-core/pull/3973
- https://github.com/powsybl/powsybl-core/commit/17461264d1d18f9bba43bb7855f251e9fa55a4db
- https://github.com/powsybl/powsybl-core/commit/7aa28d8c2492bbcd061585cb498acce72d5ed79a
- https://github.com/powsybl/powsybl-core
- https://github.com/powsybl/powsybl-core/releases/tag/v7.2.2
