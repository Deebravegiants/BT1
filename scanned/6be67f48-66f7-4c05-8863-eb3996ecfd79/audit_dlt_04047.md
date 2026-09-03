# [H] Users Can Gain Additional Vault Shares When Rolling Position Via Re-Entrancy Attack

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/104
Type: sherlock-finding

## Details
xiaoming90

high

# Users Can Gain Additional Vault Shares When Rolling Position Via Re-Entrancy Attack

## Summary

An attacker can perform a re-entrancy attack to gain additional vault shares when rolling over their position to a longer dated maturity by exploiting the roll vault position function as the checks-effects-interactions pattern is not adhered to.

## Vulnerability Detail

If the`VaultConfiguration.ALLOW_REENTRANCY` setting of a vault is set to `True`, the `VaultAccountAction.rollVaultPosition` function allows re-entrancy. Line 102 within the `VaultAccountAction.rollVaultPosition` function will set the `reentrancyStatus` back to `_NOT_ENTERED` to allow re-entrancy.

Assume that a vault allows re-entrancy and Bob (attacker) is trying to roll over its position to a longer dated maturity by calling the `VaultAccountAction.rollVaultPosition` function. Bob has 100 vault shares, so in the storage, Bob's `vaultAccount.vaultShares = 100` at this point.

At Line 105, the `VaultAccountLib.getVaultAccount` function is called to load the user's vault account data from the storage and load them onto the `vaultAccount` variable on memory. The key point to note is that `vaultAccount` variable is stored in memory.

At Line 119, the `vaultState.exitMaturity` function will be triggered to exit the current maturity by removing all existing 100 vault shares.

At Line 138, the `vaultAccount.depositForRollPosition` function will be triggered to pull the necessary deposit from Bob's address as repayment. An important point here is that within the `vaultAccount.depositForRollPosition`, it will perform a `ERC20.transferFrom` call with Bob's address in the `from` parameter. Depending on the tokens to be transferred as a deposit, some tokens will pass the control to the sender (Bob). For instance, ERC777 contains the [`tokensToSend`](https://docs.openzeppelin.com/contracts/2.x/api/token/erc777#IERC777Sender-tokensToSend-address-address-address-uint256-bytes-bytes-) hook that will call the sender when tokens are about to be moved. 

Assume that the control is passed to Bob. Bob re-enters the `VaultAccountAction.rollVaultPosition` function again, and at Line 105, the `VaultAccountLib.getVaultAccount` function is called again to load Bob's vault account data from the storage and load them onto the `vaultAccount` variable on memory. Note that Bob's `vaultAccount.vaultShares` is still `100` in storage at this point. 

Then, the `vaultState.exitMaturity` function at Line 119 will be triggered again for the second time. Note that within the `vaultState.exitMaturity` function, Bob's `vaultAccount.vaultShares` is still 100 because the state changes are not written back to the storage yet, so the math operation within the function will not revert, and it will be able to redeem the 100 vault shares successfully.

At Line 142, the `vaultAccount.borrowAndEnterVault` function will be triggered, and Bob's position will be moved to a longer dated maturity. When the inner re-entrancy call returns, the code execution flow will resume from Line 138. Subsequently, the `vaultAccount.borrowAndEnterVault` function at Line 142 will be triggered again for the second time, thus moving Bob's position to a longer dated maturity again.

At the end of the `VaultAccountAction.borrowAndEnterVault` function, the `vaultAccount` in memory is finally written back to the storage via the `vaultAccount.setVaultAccount` function. 

As such, Bob effectively gains twice the amount of vault shares by rolling over his position. Bob could gain more by repeating the re-enter multiple times while executing the attack.

A checks-effects-interactions pattern is a pattern to avoid a re-entrancy attack. Note that in terms of the checks-effects-interactions pattern:

- The process of writing the data from memory back to storage will be classified as the "effects" step.
- The process of transferring/pulling the deposit for repayment from the caller's address will be classified as the "interactions" step 

Notice that over here the classic checks-effects-interactions pattern is not followed because the "effects" step occurred at the end, after the "interactions" step. Thus, a re-entrancy attack is possible over here.

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/104_
