# [M] Plugin need to be checked on addition

## Summary
Severity: Medium
Reporter: hansfriese
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409
Type: audit-issue

## Details
# Plugin need to be checked on addition

## Summary

The plugin should be checked if it implemented the `IPlugin` when it is newly added.
NOTE: This report contains a few other low-level issues as well and the sponsor encouraged sending them grouped as a Med level.

## Vulnerability Detail

1. The function `addPlugin` at `StakingModule.sol#L409` does not check if the new `plugin` implemented the `IPlugin` interface.
   Because major functions iterates all `plugins` for various purposes, a wrong `plugin` will make the whole protocol broken.
   Although this function is restricted to `PLUGIN_EDITOR_ROLE` only and it is possible to fix by removing the wrong plugin, I rate this as a medium level vulnerability because it has a critical effect and the role is not a strict admin role.

2. Some other low-level issues

- `rescueERC20` function at `FeeBuyback.sol#L94` always return `true` while it is supposed to return `true` only when the transfer succeeds from the comments.

```solidity
/**
 * @notice Sends ERC20 tokens trapped in contract to external address
 * @dev Only an owner is allowed to make this function call
 * @param account is the receiving address
 * @param externalToken is the token being sent
 * @param amount is the quantity being sent
 * @return boolean value indicating whether the operation succeeded.
 *
 * Emits a {Transfer} event.
 */
function rescueERC20(address account, address externalToken, uint256 amount) public onlyExecutor returns (bool) {
  IERC20(externalToken).transfer(account, amount);
  return true; //@audit different from the comment
}

```

- At `StakingModule.sol#L378`, the protocol always emits `StakeChanged` events while it is supposed to be emitted only when `oldStake != newStake`.
- At `StakingModule.sol#L60`, the function `initialize` is declared as `payable` and I don't see any reasons for that.
- At `SimplePlugin.sol#L150`, the function `setIncreaser` does not check if the `newIncreaser` is different from the current `increaser` and an unnecessary event will be emitted.

## Impact

TEL coins can be stuck in plugins and it is even possible that they are forgotten.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L378
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L60
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/SimplePlugin.sol#L150

## Tool used

Manual Review

## Recommendation

1. Check the validity of the new plugin in the function `addPlugin`.
2. Check the transfer result and return it in the function `rescueERC20` of `FeeBuyback.sol`.
3. Check if `oldStake!=newStake` at `StakingModule.sol#L378`.
4. Remove `payable` keyword from the `StakingModule` initializer.
5. Check if the `newIncreaser` is different from the current `increaser` at `SimplePlugin.sol#L150`.
