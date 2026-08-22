# [M] OpenZeppelin Contracts for Cairo account cannot process transactions on Goerli

## Summary
Severity: Medium
Chain: openzeppelin-cairo-contracts
Component: openzeppelin-cairo-contracts
CVE: CVE-2022-31153
CWE: Improper Control of a Resource Through its Lifetime, Incorrect Authorization
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-8mjr-jr5h-q2xr
Type: github-advisory

## Details
### Impact
This vulnerability affects all accounts (vanilla and ethereum flavors) in the [v0.2.0 release of OpenZeppelin Contracts for Cairo](https://github.com/OpenZeppelin/cairo-contracts/releases/tag/v0.2.0), which are not whitelisted on StarkNet mainnet, so only goerli deployments of v0.2.0 accounts are affected.

This faulty behavior is not observed in [StarkNet's testing framework](https://github.com/starkware-libs/cairo-lang/blob/master/src/starkware/starknet/testing/starknet.py), so don't rely on it passing to detect this issue on custom accounts.

### Patches
This bug has been patched in [v0.2.1](https://github.com/OpenZeppelin/cairo-contracts/releases/tag/v0.2.1).

### References
The issue is detailed in https://github.com/OpenZeppelin/cairo-contracts/issues/386.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Contracts for Cairo repo](https://github.com/OpenZeppelin/cairo-contracts/issues/new/choose)
* Email us at [security@openzeppelin.com](mailto:security@openzeppelin.com)
