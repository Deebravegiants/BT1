# [H] MarbleRun unauthenticated recovery allows Coordinator impersonation

## Summary
Severity: High
Advisory: GHSA-w7wm-2425-7p2h
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-02-04
Source: https://github.com/advisories/GHSA-w7wm-2425-7p2h
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/marblerun` — affected >=0 <1.7.0

## Details
### Impact

During recovery, a Coordinator only verifies that a given recovery key decrypts the sealed state, not if this key was provided by a party with access to one of the recovery keys defined in the manifest.
This allows an attacker to manually craft a sealed state using their own recovery keys, and a manifest that does not match the rest of the state.

If network traffic is redirected from the legitimate coordinator to the attacker's Coordinator, a remote party is susceptible to impersonation if they verify the Coordinator without comparing the root certificate of the Coordinator against a trusted reference.

Under these circumstances, an attacker can trick a remote party into trusting the malicious Coordinator by presenting a manifest that does not match the actual state of the deployment.

This issue does **not** affect the following:

* secrets and state of the legitimate Coordinator instances
* integrity of workloads
* certificates chaining back to the legitimate Coordinator root certificate

### Patches

The issue has been patched in [`v1.7.0`](https://github.com/edgelesssys/marblerun/releases/tag/v1.7.0).

### Workarounds

Connections that purely authenticate based on a known Coordinator's root certificate, e.g. the one retrieved when using the `marblerun manifest set` CLI command, are not affected.

## References
- https://github.com/edgelesssys/marblerun/security/advisories/GHSA-w7wm-2425-7p2h
- https://github.com/edgelesssys/marblerun/commit/e4864f9f1d0f12a4a7d28514da43bcc75603a5b5
- https://github.com/edgelesssys/marblerun
- https://github.com/edgelesssys/marblerun/releases/tag/v1.7.0
- https://pkg.go.dev/vuln/GO-2025-3450
