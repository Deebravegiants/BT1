# [M] [ADRIRO-NEW-M-03] Safe approval could lead to a denial of service in VotiumStrategy

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/54
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategyCore.sol#L225
https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategyCore.sol#L282


# Vulnerability details

## Summary

The introduction of the SafeERC20 wrapper may lead to an accidental denial of service due to how the `safeApprove()` function works internally.

## Impact

The updated codebase uses the [SafeERC20](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20#SafeERC20) wrapper provided by the OpenZeppelin contracts library to handle ERC20 interaction in the VotiumStrategyCore contract. This was presumably added to provide safer support for the `applyRewards()` function, since this function needs to handle arbitrary tokens.

However, the SafeERC20 wrapper has been also applied as part of the CVX handling in the VotiumStrategyCore contract. This can be seen in the implementations of `depositRewards()` and `sellCvx()`:

```solidity
219:     function depositRewards(
220:         uint256 _amount,
221:         uint256 _cvxMinout
222:     ) public payable onlyManager {
223:         uint256 cvxAmount = buyCvx(_amount);
224:         if (cvxAmount < _cvxMinout) revert MinOut();
225:         IERC20(CVX_ADDRESS).safeApprove(VLCVX_ADDRESS, cvxAmount);
226:         ILockedCvx(VLCVX_ADDRESS).lock(address(this), cvxAmount, 0);
227:         trackedCvxBalance -= cvxAmount;
228:         emit DepositReward(cvxPerVotium(), _amount, cvxAmount);
229:     }
```

```solidity
276:     function sellCvx(
277:         uint256 _cvxAmountIn
278:     ) internal returns (uint256 ethAmountOut) {
279:         address CVX_ETH_CRV_POOL_ADDRESS = 0xB576491F1E6e5E62f1d8F26062Ee822B40B0E0d4;
280:         // cvx -> eth
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/54_
