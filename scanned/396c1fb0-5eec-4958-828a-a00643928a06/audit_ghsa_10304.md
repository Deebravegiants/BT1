# [M] PowerShell Command Injection in Podman HyperV Machine

## Summary
Severity: Medium
Advisory: GHSA-hc8w-h2mf-hp59
CVE: CVE-2026-33414
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-hc8w-h2mf-hp59
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v4` — affected >=4.8.0
- Go: `github.com/containers/podman/v5` — affected >=0 <5.8.2

## Details
## Summary

A command injection vulnerability exists in Podman's HyperV machine backend. The VM image path is inserted into a PowerShell double-quoted string without sanitization, allowing `$()` subexpression injection.

## Affected Code

**File**: `pkg/machine/hyperv/stubber.go:647`

```go
resize := exec.Command("powershell", []string{
    "-command",
    fmt.Sprintf("Resize-VHD \"%s\" %d", imagePath.GetPath(), newSize.ToBytes()),
}...)
```



## Root Cause

PowerShell evaluates `$()` subexpressions inside double-quoted strings before executing the outer command. The `fmt.Sprintf` call places the user-controlled image path directly into double quotes without escaping or sanitization.

## Impact

An attacker who can control the VM image path (through a crafted machine name or image directory) can execute arbitrary PowerShell commands with the privileges of the Podman process on the Windows host. On typical Windows installations, this means SYSTEM-level code execution.


## Patch

https://github.com/containers/podman/commit/571c842bd357ee626019ea97d030fb772fc654ed

The affected code is only used on Windows, all other operating systems are not affected by this and can thus ignore the CVE patch.

## Credit

We like to thank Sang-Hoon Choi (@KoreaSecurity) for reporting this issue to us.

## References
- https://github.com/containers/podman/security/advisories/GHSA-hc8w-h2mf-hp59
- https://nvd.nist.gov/vuln/detail/CVE-2026-33414
- https://github.com/containers/podman/commit/571c842bd357ee626019ea97d030fb772fc654ed
- https://github.com/containers/podman
