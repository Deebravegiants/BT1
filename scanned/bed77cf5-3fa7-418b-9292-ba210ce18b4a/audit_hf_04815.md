# [M] WrappedAerodromeAM.sol is not compatible

## Summary
Severity: Medium
Contest weight: 0.6751
Dataset id: 22685
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
From the README file: We also want to receive issues regarding minimal implementations of ERC20 Tokens, which besides a standard implementation have one of the following "weird behaviours": Revert on Zero Value.
When the owner of a position calls WrappedAerodromeAM.decreaseLiquidity, they should receive the transferred liquidity back and fees.
Let's consider the following scenario:
1) The owner of the position calls decreaseLiquidity, and they are supposed to receive fees.
```solidity
// Claim any pending fees from the Aerodrome Pool.
(uint256 fee0Pool, uint256 fee1Pool) = _claimFees(pool);
// Calculate the new fee balances.
(poolState_, positionState_) = _getFeeBalances(poolState_, positionState_, fee0Pool, fee1Pool);
```
2) Since the fee for the revert on zero transfer token is zero, a DOS will occur, and the user will not be able to decrease liquidity.
```solidity
// Pay out the fees to the position owner.
ERC20(token0[pool]).safeTransfer(msg.sender, fee0Position);
//fee0Position = 0
ERC20(token1[pool]).safeTransfer(msg.sender, fee1Position); // or fee1Position = 0
emit FeesPaid(positionId, uint128(fee0Position), uint128(fee1Position));
```
A denial-of-service (DOS) can occur on the decreaseLiquidity and claimFees functions in WrappedAerodromeAM smart contract of the revert on zero transfer token when the fee is zero value.

## Recommendation
Consider changing decreaseLiquidity and claimFees functions as follows:
```solidity
if (fee0Position != 0)
    ERC20(token0[pool]).safeTransfer(msg.sender, fee0Position);
if (fee1Position != 0)
    ERC20(token1[pool]).safeTransfer(msg.sender, fee1Position);
```
