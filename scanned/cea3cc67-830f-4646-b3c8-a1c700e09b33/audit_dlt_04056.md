# [H] Malicious User Can Steal All Assets From A Vault When Exiting The Vault By Performing A Re-Entrancy Attack

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/85
Type: sherlock-finding

## Details
xiaoming90

high

# Malicious User Can Steal All Assets From A Vault When Exiting The Vault By Performing A Re-Entrancy Attack

## Summary

An attacker can perform a re-entrancy attack against the vault to drain all its assets by exploiting the vulnerable exit vault function as the checks-effects-interactions pattern is not adhered to.

## Vulnerability Detail

If the`VaultConfiguration.ALLOW_REENTRANCY` setting of a vault is set to `True`, the `VaultAccountAction.exitVault` function allows re-entrancy. Line 183 within the `VaultAccountAction.exitVault` function will set the `reentrancyStatus` back to `_NOT_ENTERED` to allow re-entrancy.

Assume that a vault allows re-entrancy and Bob (attacker) is trying to exit the vault post-maturity after the vault has settled by calling the `VaultAccountAction.exitVault` function. Bob has 100 vault shares, so in the storage, Bob's `vaultAccount.vaultShares = 100` at this point.

At Line 186, the `VaultAccountLib.getVaultAccount` function is called to load the user's vault account data from the storage and load them onto the `vaultAccount` variable on memory. The key point to note is that `vaultAccount` variable is stored in memory.

At Line 192, the `vaultAccount.settleVaultAccount` function will settle Bob's vault account and set the `vaultAccount.vaultShares` to `0` in the memory.

At Line 204, the `vaultConfig.redeemWithDebtRepayment` function will be called to redeem all strategy tokens, and any profits will be sent back to the user. Within the `vaultConfig.redeemWithDebtRepayment` function, Ether or ERC20 tokens will be transferred to the user depending on the vault's underlying assets. The transfer will effectively pass the control back to the user. At this point, the `vaultAccount.vaultShares` is `0` in the memory, but the `vaultAccount.vaultShares` is still `100` in the storage because the `vaultAccount.setVaultAccount` has not been triggered yet to write the information stored in the memory back to the storage.

Bob re-enters the `VaultAccountAction.exitVault` function again, and at Line 186, the `VaultAccountLib.getVaultAccount` function is called again to load the user's vault account data from the storage and load them onto the `vaultAccount` variable on memory. Note that the `vaultAccount.vaultShares` is still `100` in storage at this point. Therefore, in this context, the `vaultAccount.vaultShares` in the memory will be `100,` and the vault will redeem the 100 vault shares again and transfer the profits to Bob again.

Bob repeats the above steps multiple times until all the assets in the vault are drained.

At the end of the `VaultAccountAction.exitVault` function at Line 247, the `vaultAccount` in memory is finally written back to the storage via the `vaultAccount.setVaultAccount` function. 

A checks-effects-interactions pattern is a pattern to avoid a re-entrancy attack. Note that in terms of the checks-effects-interactions pattern:

- The process of writing the data from memory back to storage will be classified as the "effects" step.
- The process of transferring the profit back to users will be classified as the "interactions" step 

Notice that over here the classic checks-effects-interactions pattern is not followed because the "effects" step occurred at the end, after the "interactions" step. Thus, a re-entrancy attack is possible over here.

https://github.com/sherlock-audit/2022-09-notional/blob/main/contracts-v2/contracts/external/actions/VaultAccountAction.sol#L169

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/85_
