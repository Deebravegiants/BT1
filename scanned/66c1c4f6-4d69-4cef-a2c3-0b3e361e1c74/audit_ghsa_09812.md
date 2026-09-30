# [H] Fleet Affected by Local Privilege Escalation via Tcl Command Injection in Orbit

## Summary
Severity: High
Advisory: GHSA-rphv-h674-5hp2
CVE: CVE-2026-27806
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-rphv-h674-5hp2
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.1

## Details
## Summary

The Orbit agent's FileVault disk encryption key rotation flow on collects a local user's password via a GUI dialog and interpolates it directly into a Tcl/expect script executed via `exec.Command("expect", "-c", script)`. Because the password is inserted into Tcl brace-quoted `send {%s}`, a password containing `}` terminates the literal and injects arbitrary Tcl commands. Since Orbit runs as root, this allows a local unprivileged user to escalate to root privileges.

## CWE

- **CWE-78**: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
- **CWE-94**: Improper Control of Generation of Code ('Code Injection')

## Impact

- Local privilege escalation to root: Any unprivileged local user on a managed endpoint can execute arbitrary commands as root

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-rphv-h674-5hp2
- https://github.com/fleetdm/fleet
