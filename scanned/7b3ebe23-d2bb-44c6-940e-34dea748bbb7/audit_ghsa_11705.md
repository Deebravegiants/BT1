# [M] PinchTab: OS Command Injection via Profile Name in Windows Cleanup Routine Enables Arbitrary Command Execution

## Summary
Severity: Medium
Advisory: GHSA-p8mm-644p-phmh
CVE: CVE-2026-33623
CWE: CWE-400, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-p8mm-644p-phmh
Type: github-advisory

## Affected
- Go: `github.com/pinchtab/pinchtab/cmd/pinchtab` — affected >=0 <0.8.5
- Go: `github.com/pinchtab/pinchtab` — affected >=0 <0.8.5

## Details
### Summary
PinchTab `v0.8.4` contains a Windows-only command injection issue in the orphaned Chrome cleanup path. When an instance is stopped, the Windows cleanup routine builds a PowerShell `-Command` string using a `needle` derived from the profile path. In `v0.8.4`, that string interpolation escapes backslashes but does not safely neutralize other PowerShell metacharacters.

If an attacker can launch an instance using a crafted profile name and then trigger the cleanup path, they may be able to execute arbitrary PowerShell commands on the Windows host in the security context of the PinchTab process user.

This is not an unauthenticated internet RCE. It requires authenticated, administrative-equivalent API access to instance lifecycle endpoints, and the resulting command execution inherits the permissions of the PinchTab OS user rather than bypassing host privilege boundaries.

### Details
**Issue 1 — PowerShell command string built with interpolated user-influenced data (`internal/bridge/cleanup_windows.go` in `v0.8.4`):**

```
func findPIDsByPowerShell(needle string) []int {
    escaped := strings.ReplaceAll(needle, `\`, `\\`)
    cmd := exec.Command("powershell", "-NoProfile", "-Command",
        fmt.Sprintf(`Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | `+
            `Where-Object { $_.CommandLine -like '*%s*' } | `+
            `Select-Object -ExpandProperty ProcessId`, escaped))
}
```

The `needle` value is interpolated directly into a PowerShell command string. Escaping backslashes alone is not sufficient to make arbitrary user-controlled content safe inside a PowerShell expression.

**Issue 2 — `needle` is derived from launchable profile names:**

The cleanup path uses:

```
findPIDsByPowerShell(fmt.Sprintf("--user-data-dir=%s", profileDir))
```

The profile directory is derived from the instance/profile name used during launch. In `v0.8.4`, profile name validation rejected path traversal characters such as `/`, `\`, and `..`, but it did not comprehensively block PowerShell metacharacters such as single quotes or statement separators.

**Issue 3 — Trigger path is reachable through normal instance lifecycle APIs:**

The attack path described in the report uses:

1. `POST /instances/launch` with a crafted `name`
2. `POST /instances/{id}/stop` to trigger the cleanup routine

That means exploitability depends on access to privileged orchestration endpoints, not on local shell access.

### PoC
**Environment assumptions**

- PinchTab `v0.8.4`
- Windows host
- Valid API token with access to instance lifecycle endpoints

**Example sequence**

```bash
curl -X POST http://HOST:9867/instances/launch \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "poc'\''; Start-Process calc; $x='\''",
    "mode": "headless"
  }'
```

Then:

```bash
curl -X POST http://HOST:9867/instances/<INSTANCE_ID>/stop \
  -H "Authorization: Bearer <TOKEN>"
```

If the payload survives the launch path and reaches the vulnerable cleanup code, the injected PowerShell executes when the Windows cleanup routine runs.

### Impact
1. Arbitrary PowerShell command execution on Windows as the PinchTab process user.
2. Full compromise of data and processes accessible to that user account.
3. Possible persistence or host-level follow-on actions within the same user security context.
4. Potential repeated execution in restart-heavy environments if the vulnerable cleanup path is triggered repeatedly.

### Scope And Limits
1. Windows only.
2. Requires authenticated, administrative-equivalent API access to instance lifecycle endpoints.
3. Does not by itself elevate beyond the privileges of the Windows user running PinchTab.
4. This is stronger than a policy bypass or low-risk hardening gap, but narrower than unauthenticated remote code execution.

### Suggested Remediation
1. Do not interpolate user-influenced values into PowerShell `-Command` strings.
2. Pass search terms through environment variables or structured arguments instead of code generation.
3. Keep strict validation on profile names, but do not rely on input validation alone as the primary defense.
4. Add regression tests covering PowerShell metacharacters in profile-derived values on Windows.




### **Steps to Reproduce:**

**Environment Setup:**
Target: PinchTab v0.8.4 (Windows build)
Platform: Windows only

**1. Launch Instance with Malicious Profile Name**

```
curl -X POST http://[server-ip]:9867/instances/launch \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "poc'\''; Start-Process calc; $x='\''",
    "mode": "headless"
  }'
```

**2. Stop Instance to Trigger Injection**

```
curl -X POST http://[server-ip]:9867/instances/<INSTANCE_ID>/stop \
  -H "Authorization: Bearer <TOKEN>"
```

### **Additional Observation — Repeated Execution (DoS Amplification)**

**In environments where instances are automatically restarted (e.g., always-on mode), the cleanup routine is triggered repeatedly.**

Because the injection occurs during cleanup, the payload is executed on every restart cycle:
Continuous spawning of calc.exe processes
Resource exhaustion
System instability or crash

### **Impact**

This vulnerability allows an authenticated attacker to execute arbitrary PowerShell commands on the Windows host running PinchTab. Impact - full host compromise including command execution, persistence, and data access; Root Cause - user-controlled input (profile name) is embedded into a PowerShell command without proper neutralization of special characters; Remediation - avoid constructing shell commands using string interpolation, enforce strict input validation (allowlist), and use structured command execution instead of powershell -Command.

Additionally, because the injection is triggered during the cleanup routine, environments with automatic instance restart behavior may repeatedly execute the injected payload, leading to uncontrolled process creation and resource exhaustion. This enables a reliable denial-of-service condition in addition to remote code execution.

## References
- https://github.com/pinchtab/pinchtab/security/advisories/GHSA-p8mm-644p-phmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33623
- https://github.com/pinchtab/pinchtab/commit/25b3374bdcdf0dad32c44d5d726bf953238cd8bd
- https://github.com/pinchtab/pinchtab
