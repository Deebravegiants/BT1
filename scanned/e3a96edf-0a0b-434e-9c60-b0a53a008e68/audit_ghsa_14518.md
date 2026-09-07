# [H] Constellation allows Emergency shell access during initramfs boot phase

## Summary
Severity: High
Advisory: GHSA-6w5f-5wgr-qjg5
Ecosystem: Go
Published: 2023-03-09
Source: https://github.com/advisories/GHSA-6w5f-5wgr-qjg5
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/constellation/v2` — affected >=0 <2.6.0

## Details
### Impact

An active attacker could let the boot fail on purpose in the initramfs, dropping the serial console into an emergency shell. This gives attackers with access to the serial console full control over the VM.

### Patches

The issue has been patched in [v2.6.0](https://github.com/edgelesssys/constellation/releases/tag/v2.6.0).

### Workarounds

none

## References
- https://github.com/edgelesssys/constellation/security/advisories/GHSA-6w5f-5wgr-qjg5
- https://github.com/edgelesssys/constellation
- https://github.com/edgelesssys/constellation/releases/tag/v2.6.0
