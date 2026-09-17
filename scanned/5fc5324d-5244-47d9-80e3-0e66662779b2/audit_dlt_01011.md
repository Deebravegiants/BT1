# [C] Cosmos EVM Vulnerability

## Summary
Severity: Critical
Chain: github.com/cosmos/evm
Component: github.com/cosmos/evm, github.com/cosmos/evm
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-8pfh-j44r-f654
Type: github-advisory

## Details
## Patches
Patched in versions `v0.3.1`, `v0.4.2`, and in the `v0.5.0` release. More information will be disclosed at a later point to ensure chains have time to safely upgrade.

## Workarounds
No workarounds for chains that make use of static or dynamic precompiles. Upgrading is strongly recommended.

## Testing
Tests are introduced in every affected version.

## Credits
Special thanks to @yihuang for the help on this issue.
