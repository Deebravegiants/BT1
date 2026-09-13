# [H] Rounding up in minting shares

## Summary
Severity: High
Source: https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L392
Type: audit-issue

## Details
When processing the queued deposits, shares are minted to the receiver in the queue according to the amount of assets deposited. However, the amount of shares minted is always [rounded up](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L392). This means that one can always receive 1 vault share with a 1-wei deposit.

As the vault is expected to be increasing in value from yield rewards, 1 vault share will be worth more than 1 wei asset eventually. A malicious user can spam the deposit queue with 1-wei deposit from many accounts to get 1 share each and then redeem them for more assets when each share is worth more.

Consider rounding down when minting vault shares.

**Update:** _Fixed in [PR#46](https://github.com/pods-finance/yield-contracts/pull/46), with commit `5ac5e3c` being the last one added._
