# [M] `StargateStrategy#_currentBalance` calculation is incorrect and may lead to DoS

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1520
Type: code-finding

## Details
# Lines of code

 https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateStrategy.sol#L245-L246
 https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateStrategy.sol#L216


# Vulnerability details

## Impact

In `StargateStrategy`, `_currentBalance` is used to determine the total collateral in terms of WETH. It is used in `_withdraw` to check whether the contract is solvent enough to process the withdrawal. However a miscalculation may lead to the returned value being less than the actual value, which can cause `_withdraw` to revert when it ought not to, preventing users from withdrawing and trapping funds in the contract. This would likely arise when a user attempts to withdraw all funds from the contract, for instance if they are the last user to withdraw from a strategy (e.g. if it is being deprecated).

## Proof of Concept

`_currentBalance` fetches the amount of WETH in the contract (`queued`), the amount of LP tokens staked in the `lpStaking` contract (`amount`), and the amount of claimable rewards (`claimableRewards`), returning the sum of these values.

```solidity
File: tapioca-yieldbox-strategies-audit\contracts\stargate\StargateStrategy.sol

214:     function _currentBalance() internal view override returns (uint256 amount) {
215:         uint256 queued = wrappedNative.balanceOf(address(this));
216:         (amount, ) = lpStaking.userInfo(lpStakingPid, address(this)); // @audit this returns amount of LP tokens, not WETH
217:         uint256 claimableRewards = compoundAmount();
218:         return amount + queued + claimableRewards;
219:     }
```

While `queued` and `claimableRewards` refer to amounts of WETH, `amount` refers to the amount of LP tokens staked, as is described in Stargate's [LPStaking.sol](https://github.com/stargate-protocol/stargate/blob/main/contracts/LPStaking.sol#L22) contract. The amount of LP tokens staked is realistically never going to be equal to the amount of WETH used to acquire them, and so a discrepency exists.

Assume that `_currentBalance` returns a smaller value than the actual collateral amount of the contract (note: in a separate medium severity finding of mine titled "`StargateStrategy#_withdraw`: ether becomes trapped in the contract whenever a user withdraws", it is shown that 1 LP token < 1 WETH in value in the test environment of this repo). 

When a user calls `YieldBox#withdraw` to withdraw funds from Stargate, `StargateStrategy#_withdraw` is executed and the check on line 246 may incorrectly cause a revert, preventing the user from accessing their funds. While this won't be an issue if there are many users utilising the strategy at the time, it will eventually become a problem for the unlucky user who is last to withdraw from the strategy.

```solidity
File: tapioca-yieldbox-strategies-audit\contracts\stargate\StargateStrategy.sol

241:     function _withdraw(
242:         address to,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1520_
