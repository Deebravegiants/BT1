# [C] Transparent TLS may not be applied to Marbles with certain manifest configurations

## Summary
Severity: Critical
Advisory: GHSA-x5r5-2qrx-rqj8
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-x5r5-2qrx-rqj8
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/marblerun` — affected >=0 <1.4.1

## Details
Transparent TLS (TTLS) is a MarbleRun feature that wraps plain TCP connections between Marbles in TLS.
In the manifest, a user defines the connections that should be considered.

### Impact
If a Marble is configured for TTLS, but doesn't have an environment variable defined in its parameters, TTLS is not applied.
The traffic will not be encrypted.

MarbleRun deployments that don't use TTLS (which is only available with EGo Marbles) are not affected.

### Patches
The issue has been patched in [`v1.4.1`](https://github.com/edgelesssys/marblerun/releases/tag/v1.4.1).

### Workarounds
Make sure that all Marbles that use TTLS have an environment variable defined in their parameters.

### References
For a description of TTLS, see <https://docs.edgeless.systems/marblerun/features/transparent-TLS>
See the updated section on TTLS configuration in the manifest: <https://docs.edgeless.systems/marblerun/workflows/define-manifest#tls>

## References
- https://github.com/edgelesssys/marblerun/security/advisories/GHSA-x5r5-2qrx-rqj8
- https://github.com/edgelesssys/marblerun/commit/0330ced092253613a07abe7b330ff6ac6fc6e9c6
- https://github.com/edgelesssys/marblerun/commit/e5bcfe32883d22f3d87ffc9400f9fdb5ecbe3200
- https://github.com/edgelesssys/marblerun
- https://github.com/edgelesssys/marblerun/releases/tag/v1.4.1
