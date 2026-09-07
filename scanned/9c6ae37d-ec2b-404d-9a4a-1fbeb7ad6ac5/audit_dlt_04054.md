# [H] Assets In A Vault Account That Needs To Be Deleveraged Can Be Stolen Via Re-Entrancy Attack

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/87
Type: sherlock-finding

## Details
xiaoming90

high

# Assets In A Vault Account That Needs To Be Deleveraged Can Be Stolen Via Re-Entrancy Attack

## Summary

An attacker can perform a re-entrancy attack against a vault account that needs to be deleveraged to steal all the assets within it by exploiting the vulnerable deleverage account function as the checks-effects-interactions pattern is not adhered to.

## Vulnerability Detail

If the`VaultConfiguration.ALLOW_REENTRANCY` setting of a vault is set to `True`, the `VaultAccountAction.deleverageAccount` function allows re-entrancy. The `VaultAccountAction._authenticateDeleverage` function called at Line 269 of the `VaultAccountAction.deleverageAccount` function will set the `reentrancyStatus` back to `_NOT_ENTERED` to allow re-entrancy.

Assume the following:

- A vault allows re-entrancy and Bob (attacker) is trying to deleverage Alice's account
- Alice has 100 vault shares, so in the storage, Bob's `vaultAccount.vaultShares = 100` at this point
- 30 of Alice's vault shares need to be deleveraged/liquidated to bring her account back to healthy collateral ratio

Bob calls the `VaultAccountAction.deleverageAccount` function in an attempt to deleverage 30 of Alice's vault shares with the appropriate amount of cash/deposit.

At Line 270, the `VaultAccountLib.getVaultAccount` function is called to load Alice's vault account data from the storage and load them onto the `vaultAccount` variable on memory. The key point to note is that `vaultAccount` variable is stored in memory. Alice's `vaultAccount.vaultShares = 100` at this point.

At Line 284, the `VaultAccountAction._depositLiquidatorAmount` function will be triggered to pull the deposit from Bob's address. An important point here is that within the `VaultAccountAction._depositLiquidatorAmount`, it will perform a `ERC20.transferFrom` call with Bob's address in the `from` parameter. Depending on the tokens to be transferred as a deposit, some tokens will pass the control to the sender (Bob). For instance, ERC777 contains the [`tokensToSend`](https://docs.openzeppelin.com/contracts/2.x/api/token/erc777#IERC777Sender-tokensToSend-address-address-address-uint256-bytes-bytes-) hook that will call the sender when tokens are about to be moved. 

Assume that the control is passed to Bob. Bob re-enters the `VaultAccountAction.deleverageAccount` function again, and at Line 270, the `VaultAccountLib.getVaultAccount` function is called again to load Alice's vault account data from the storage and load them onto the `vaultAccount` variable on memory. Note that Alice's `vaultAccount.vaultShares` is still `100` in storage at this point.  Therefore, in this context, the `vaultAccount.vaultShares` in the memory will be `100`. The `calculateCollateralRatio` function at Line 277 will perform is calculated based on the fact that Alice still holds 100 vault shares and determine that 30 of Alice's vault shares need to be deleveraged to bring her account back to healthy collateral ratio. Therefore, Bob can deleverage 30 of Alice's vault shares again for a second time.

Bob repeats the above steps multiple times until all of Alice's assets are drained.

At the end of the `VaultAccountAction.deleverageAccount` function at Line 317, the `vaultAccount` in memory is finally written back to the storage via the `vaultAccount.setVaultAccount` function. 

Finally, Alice's vault shares or assets will be transferred to Bob in lines 321-328.

A checks-effects-interactions pattern is a pattern to avoid a re-entrancy attack. Note that in terms of the checks-effects-interactions pattern:

- The process of writing the data from memory back to storage will be classified as the "effects" step.
- The process of transferring/pulling the deposit from the caller's address will be classified as the "interactions" step 

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/87_
