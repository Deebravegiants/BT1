# [H] Incorrect Account Used for Signing

## Summary
Severity: High
Chain: eth-ledger-bridge-keyring
Component: eth-ledger-bridge-keyring, @metamask/eth-ledger-bridge-keyring
CWE: Improper Authentication
Published: 2020-03-24
Source: https://github.com/advisories/GHSA-vg44-fw64-cpjx
Type: github-advisory

## Details
### Impact

Anybody using this library to sign with a BIP44 account other than the first account may be affected. If a user is signing with the first account (i.e. the account at index `0`), or with the legacy MEW/MyCrypto HD path, they are not affected.

The vulnerability impacts cases where the user signs a personal message or transaction without first adding the account. This includes cases where the user has already added the account in a previous session (i.e. they added the account, reset the application, then signed something). The serialization/deserialization process does restore a previously added account, but it doesn&#39;t restore the index instructing the keyring to use that account for signing. As a result, after serializing then deserializing the keyring state, the account at index `0` is always used for signing even if it isn&#39;t the current account.

### Patches

This has been patched ([#14](https://github.com/MetaMask/eth-ledger-bridge-keyring/pull/14)) in version &gt;=0.2.1 of [`eth-ledger-bridge-keyring`](https://www.npmjs.com/package/eth-ledger-bridge-keyring), and in version &gt;=0.2.2 of [`@metamask/eth-ledger-bridge-keyring`](https://www.npmjs.com/package/@metamask/eth-ledger-bridge-keyring). Users are encouraged to migrate to the new package name.

### Workarounds

To work around this problem without updating, you should remove then re-add the account before use. As long as the account was added during the lifetime of that process, signing with that account should work correctly.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [MetaMask/eth-ledger-bridge-keyring on GitHub](https://github.com/MetaMask/eth-ledger-bridge-keyring)
* Email the MetaMask team at [hello@metamask.io](mailto:hello@metamask.io)
