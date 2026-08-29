# [H] Certain custom networks vulnerable to chosen chainId attack

## Summary
Severity: High
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2021-01-25
Source: https://github.com/MetaMask/metamask-extension/security/advisories/GHSA-c2xw-px2x-pr65
Type: github-advisory

## Details
_Note:_ As of January 25, 2021, this vulnerability has been addressed in the latest version of MetaMask on all platforms. To the best of our knowledge, this attack was never exploited in the wild.

### Impact

In version `8.0.x` and lower of the MetaMask extension, if a user adds a custom network to MetaMask without specifying a chain ID, MetaMask requests `net_version` from the network's RPC endpoint at runtime, and uses the return value to sign transactions.

This can induce the user to sign transactions for unintended chains in the following ways:

1. `net_version` returns the network ID, which may differ the chain ID. Transactions signed with a network ID could be invalid for the intended chain, and valid for another. See [EIP-155](https://eips.ethereum.org/EIPS/eip-155) for details.
2. A malicious or faulty endpoint could return arbitrary results for `net_version` at runtime.

Any user of MetaMask version `8.0.x` and lower that adds or has added a custom network without specifying a chain ID is vulnerable to this attack.

### Patches

Version `>=8.1.0` includes 088d4c34f112eb0f638ce99dae5c0d0958569038.

### Workarounds

- Update the MetaMask extension to version `>=8.1.0` as soon as it's available on your platform. For most users, this will already have been done automatically. 
  - Version `>=8.1.0` requires `chainId` values to be specified by the user for all custom networks, and MetaMask will only use those values to sign transactions.

### References

- [EIP-155](https://eips.ethereum.org/EIPS/eip-155)
- [Corresponding vulnerability on MetaMask Mobile](https://github.com/MetaMask/metamask-mobile/security/advisories/GHSA-996m-jhjg-3chr)

### For more information

If you have any questions or comments about this advisory:
- Open an issue in [MetaMask/metamask-extension](https://github.com/MetaMask/metamask-extension/issues)
- Email us at [support@metamask.io](mailto:support@metamask.io)
