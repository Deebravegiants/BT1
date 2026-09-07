# [M] MetaMask SDK indirectly exposed via malicious debug@4.4.2 dependency

## Summary
Severity: Medium
Chain: @metamask/sdk
Component: @metamask/sdk, @metamask/sdk-react, @metamask/sdk-communication-layer
CWE: Embedded Malicious Code
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-qj3p-xc97-xw74
Type: github-advisory

## Details
### Who is affected?
This advisory only applies to developers who use MetaMask SDK in the browser and who, on Sept 8th 2025 between 13:00–15:30 UTC, performed one of the following actions and then deployed their application:
- Installed MetaMask SDK into a project with a lockfile for the first time
- Installed MetaMask SDK in a project without a lockfile
- Updated a lockfile to pull in `debug@4.4.2` (e.g., via `npm update` or `yarn upgrade`)

### What happened?
On Sept 8th, 2025 (13:00–15:30 UTC), a malicious version of the `debug` package (v4.4.2) was published to npm. The injected code attempts to interfere with dApp-to-wallet communication when executed in a browser context. 

While MetaMask SDK itself was not directly impacted, projects installing the SDK during this window may have inadvertently pulled in the malicious version of `debug`.

### Mitigation
- If your application was rebuilt and redeployed after Sept 8th, 2025, 15:30 UTC, the malicious version of debug should no longer be present. Please also verify that your package manager (npm, yarn, pnpm, etc.) is not caching `debug@4.4.2`.
- If you have not yet deployed since performing one of the actions above, delete your `node_modules` and reinstall dependencies before deploying.
- If your application was deployed during the attack window and has not been rebuilt since, perform a clean install of dependencies and redeploy to ensure the malicious package is removed.

### Resources
[GitHub Advisory for debug](https://github.com/advisories/GHSA-8mgj-vmr8-frr6)
