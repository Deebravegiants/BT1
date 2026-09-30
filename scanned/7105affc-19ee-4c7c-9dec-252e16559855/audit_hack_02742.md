# [M] Privileged function on the liquidity exit

## Summary
Severity: Medium
Reporter: defsec
Source: https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L492
Type: audit-issue

## Details
# Privileged function on the liquidity exit

## Summary

On the TrueFi strategy, [liquidExitPenalty](https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L492) is paid when liquidity exited from the pool. However, the function is privileged with onlyOwner.  Up to %10 percent fee can be paid but depends on admin action. 

## Vulnerability Detail

On the TrueFi strategy, [liquidExitPenalty](https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L492) is paid when liquidity exited from the pool. However, the function is privileged with onlyOwner.  Up to %10 percent fee can be paid but depends on admin action.  There is no slippage check when liquidity is exited. 

## Impact

Funds can be lost. 

## Code Snippet

https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L492

```solidity

    /**
     * @dev Exit pool only with liquid tokens
     * This function will only transfer underlying token but with a small penalty
     * Uses the sync() modifier to reduce gas costs of using strategy and lender
     * @param amount amount of pool liquidity tokens to redeem for underlying tokens
     */
    function liquidExit(uint256 amount) external sync {
        require(block.number != latestJoinBlock[tx.origin], "TrueFiPool: Cannot join and exit in same block");
        require(amount <= balanceOf(msg.sender), "TrueFiPool: Insufficient funds");

        uint256 amountToWithdraw = poolValue().mul(amount).div(totalSupply());
        amountToWithdraw = amountToWithdraw.mul(liquidExitPenalty(amountToWithdraw)).div(BASIS_PRECISION);
        require(amountToWithdraw <= liquidValue(), "TrueFiPool: Not enough liquidity in pool");

        // burn tokens sent
        _burn(msg.sender, amount);

        ensureSufficientLiquidity(amountToWithdraw);

        token.safeTransfer(msg.sender, amountToWithdraw);

        emit Exited(msg.sender, amountToWithdraw);
    }
```
## Tool used

Manual Review

## Recommendation

The system can be ensure that LQ exited amount is suitable for the TrueFi strategy.
