# [C] Cosmos EVM Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8pfh-j44r-f654
Ecosystem: Go
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-8pfh-j44r-f654
Type: github-advisory

## Affected
- Go: `github.com/cosmos/evm` — affected >=0.3.0 <0.3.2
- Go: `github.com/cosmos/evm` — affected >=0.4.0 <0.4.2

## Details
## Patches
Patched in versions `v0.3.1`, `v0.4.2`, and in the `v0.5.0` release. More information will be disclosed at a later point to ensure chains have time to safely upgrade.

## Workarounds
No workarounds for chains that make use of static or dynamic precompiles. Upgrading is strongly recommended.

## Testing
Tests are introduced in every affected version.

## Credits
Special thanks to @yihuang for the help on this issue.

## References
- https://github.com/cosmos/evm/security/advisories/GHSA-8pfh-j44r-f654
- https://github.com/cosmos/evm/commit/79089feebe79ce1f35250ba457cbd436e6bfff8b
- https://github.com/cosmos/evm
