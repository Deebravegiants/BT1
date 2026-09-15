# [H] Contrast's unauthenticated recovery allows Coordinator impersonation

## Summary
Severity: High
Advisory: GHSA-vqv5-385r-2hf8
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-02-05
Source: https://github.com/advisories/GHSA-vqv5-385r-2hf8
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/contrast` — affected >=0 <1.4.1

## Details
### Impact

Recovering coordinators do not verify the seed provided by the recovering party. This allows an attacker to set up a coordinator with a manifest that passes validation, but with a secret seed controlled by the attacker. 

If network traffic is redirected from the legitimate coordinator to the attacker's coordinator, a workload owner is susceptible to impersonation if either 

* they `set` a new manifest and don't compare the root CA cert with the existing one (this is the default of the `contrast` CLI) or
* they `verify` the coordinator and don't compare the root CA cert with a trusted reference.

Under these circumstances, the attacker can:

* Issue certificates that chain back to the attacker coordinator's root CA.
* Recover arbitrary workload secrets of workloads deployed after the attack.

This issue does **not** affect the following:

* secrets of the legitimate coordinator (seed, workload secrets, CA)
* integrity of workloads, even when used with the rogue coordinator
* certificates chaining back to the mesh CA

### Patches

This issue is patched in Contrast v1.4.1.

### Workarounds

The issue can be avoided by verifying the coordinator root CA cert against expectations.

* At the first `set` call, keep a copy of the CA cert returned by the coordinator.
* After subsequent `set` or `verify` calls, compare the returned CA cert with the backup copy. If it matches bit-for-bit, the coordinator is legitimate.

## References
- https://github.com/edgelesssys/contrast/security/advisories/GHSA-vqv5-385r-2hf8
- https://github.com/edgelesssys/contrast
- https://pkg.go.dev/vuln/GO-2025-3455
