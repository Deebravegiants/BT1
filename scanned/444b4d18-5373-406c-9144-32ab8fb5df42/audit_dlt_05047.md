# [H] Drainage of FeeCollector's Block Transaction Fees

## Summary
Severity: High
Chain: Cronos
Component: crypto-org-chain/cronos
CVE: CVE-2021-43839
Published: 2021-12-21
Source: https://github.com/crypto-org-chain/cronos/security/advisories/GHSA-f854-hpxv-cw9r
Type: github-advisory

## Details
### Impact
In Cronos nodes running versions before v0.6.5, it is possible to take transaction fees from Cosmos SDK's FeeCollector for the current block by sending a custom crafted MsgEthereumTx.

User funds and balances are safe.


### Patches
This problem has been patched in Cronos v0.6.5 on the mempool level.
The next network upgrade with consensus-breaking changes will patch it on the consensus level.

### Workarounds
There are no tested workarounds. All validator node operators are recommended to upgrade to Cronos v0.6.5 at their earliest possible convenience.

### Credits
Thank you to @zb3 for reporting this issue on [Cronos Immunefi Bug Bounty Program](https://immunefi.com/bounty/cronos/), to @cyril-crypto for reproducing the issue and to @yihuang and @thomas-nguy for patching the issue on the CheckTx (mempool) and the DeliverTx (consensus) levels.

### For more information
If you have any questions or comments about this advisory:
* Open a discussion in [crypto-org-chain/cronos](https://github.com/crypto-org-chain/cronos/discussions/new)
* Email us at [chain@crypto.org](mailto:chain@crypto.org)
