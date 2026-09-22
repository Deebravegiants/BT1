# [M] TrueFiStrategy's liquidExit call can be front run with user's redeemNFT for exit penalty minimization

## Summary
Severity: Medium
Reporter: hyh
Source: https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L572-L585
Type: audit-issue

## Details
# TrueFiStrategy's liquidExit call can be front run with user's redeemNFT for exit penalty minimization

## Summary

Manual TrueFiStrategy's liquidExit() calls worsen liquidity situation in the linked TrueFiPool, so a user can front run them to optimize the fees, while maximizing the time spend staked for return enhancement. Such user will have his fees reduced at the expense of all other stakers, who will have to pay higher fees right after liquidExit().

## Vulnerability Detail

TrueFiStrategy's _balanceOf(), that determines the user's payout, and liquidExit(), that withdraws funds from tfUSDC to USDC, will be generally called at the different times, yielding different exit penalty values. The penalty user pays as a result of _balanceOf() mechanics assumes all tfUSDC holdings to be withdrawn now, will most of the times be greater than the penalty TrueFiStrategy pays on the actual withdrawals with liquidExit(), which mostly will be partial (i.e. only some tfUSDC be exited to support current USDC liquidity of the TrueFiStrategy).

This can be gamed by a user tuning the exit moment to catch the minimum penalty.

Underlying reason here is that while liquidExit() moves liquidity from the TrueFiPool to TrueFiStrategy it should worsen the TrueFiPool liquidity situation as some liquid assets were removed, so their share became less. The liquidity exit fee will be pushed somewhat higher as a result of `liquidExit(_amount)` call, proportionally to the `_amount`. A user that wants to unstake can front run the liquidExit() call for gaining advantage from the current mechanics by lowering the exit fee at the expense of all other users.

## Impact

A user front running the manual liquidExit() calls will have its exit fee reduced at the expense of all other stakers. I.e. users who exit early will have lesser exit fees, but also lesser interest, while it's vice versa for users who exit later. A user front running the liquidExit() call optimizes this locally in the fee/interest terms, gaining advantage at the expense of idle long-term stakers.

The net impact is fee stealing by the shorter term front-running stakers from the long-term ones.

## Code Snippet

As an example, say Bob the savvy user has his lockup ended and can now call redeemNFT(). Instead of doing this right away he monitors the `liquidExitPenalty(totalAmount)` of the TrueFiPool, where `totalAmount = (tfUSDC.poolValue() * (_viewTfUsdcStaked() + tfUSDC.balanceOf(address(this)))) / tfUSDC.totalSupply()`, i.e. the USDC equivalent of the total TrueFiStrategy tfUSDC holdings. Say he does this as a part of more complex approach, and we focus only on TrueFiStrategy part here.

Suppose Bob observed that currently liquidValue() tend to rise and TrueFiStrategy's liquidExitPenalty() drifts lower over time with TrueFiPool gaining TVL (if Sherlock gains TVL with the same pace the share of TrueFiStrategy in TrueFiPool will decline as Sherlock's TVL is distributed across many strategies). He can wait until this no longer holds or until he observes Owner's liquidExit() call in mempool, which he can front run with his redeemNFT() transaction, effectively exiting with the locally lowest exit penalty.

Another option for Bob is front-running TrueFiPool2's `borrow(amount)` on observing `amount` to be big enough. As this is one of the agencies borrows from the pool, it moves the funds from the liquid part (token balance) to the illiquid part (`creditAgency` or `ftlAgency` balance):

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L572-L585

```solidity
    /**
     * @dev Remove liquidity from strategy if necessary and transfer to lender
     * @param amount amount for lender to withdraw
     */
    function borrow(uint256 amount) external override onlyAgencies {
        require(amount <= liquidValue(), "TrueFiPool: Insufficient liquidity");
        if (amount > 0) {
            ensureSufficientLiquidity(amount);
        }

        token.safeTransfer(msg.sender, amount);

        emit Borrow(msg.sender, amount);
    }
```

On borrow() funds are moved from liquidValue() to creditValue() or loansValue():

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L387-L390

```solidity
    function poolValue() public view override returns (uint256) {
        // this assumes defaulted loans are worth their full value
        return liquidValue().add(loansValue()).add(deficitValue()).add(creditValue()).add(debtValue);
    }
```

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L403-L428

```solidity
    /**
     * @dev Return pool credit line value
     * @return pool credit value
     */
    function creditValue() public view returns (uint256) {
        if (address(creditAgency) == address(0)) {
            return 0;
        }
        return creditAgency.poolCreditValue(ITrueFiPool2(this));
    }

    /**
     * @dev Virtual value of loan assets in the pool
     * Will return cached value if inSync
     * @return Value of loans in pool
     */
    function loansValue() public view returns (uint256) {
        if (inSync) {
            return loansValueCache;
        }
        uint256 lenderLoansValue = 0;
        if (address(lender) != address(0)) {
            lenderLoansValue = lender.value(this);
        }
        return lenderLoansValue.add(ftlAgency.value(this));
    }
```

Bob's redeemNFT() is processed with the TrueFiStrategy requesting TrueFiPool2 for current fee as if the whole TrueFiStrategy's tfUSDC holdings are withdrawn:

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/Sherlock.sol#L482-L499

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/Sherlock.sol#L475-L480

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/Sherlock.sol#L159-L164

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/base/BaseNode.sol#L205-L207

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L134-L147

liquidExitPenalty() heavily depends on what share of TrueFiPool2 holdings are liquid at the moment:

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L505-L518

```solidity
    /**
     * @dev Penalty (in % * 100) applied if liquid exit is performed with this amount
     * returns BASIS_PRECISION (10000) if no penalty
     */
    function liquidExitPenalty(uint256 amount) public view returns (uint256) {
        uint256 lv = liquidValue();
        uint256 pv = poolValue();
        if (amount == pv) {
            return BASIS_PRECISION;
        }
        uint256 liquidRatioBefore = lv.mul(BASIS_PRECISION).div(pv);
        uint256 liquidRatioAfter = lv.sub(amount).mul(BASIS_PRECISION).div(pv.sub(amount));
        return BASIS_PRECISION.sub(averageExitPenalty(liquidRatioAfter, liquidRatioBefore));
    }
```

Manual TrueFiStrategy's liquidExit() removes the liquidity, worsening the situation for all subsequent exiting users:

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L155-L185

## Tool used

Manual Review

## Recommendation

As borrow() example shows the exit fee dynamics comes with the current TrueFi design, and only partial remediation looks to be achievable at the moment.

One possible approach is to make liquidExit() semi-automatic and tied to user's withdraw (as it is done for other strategies), as an example keeping the predefined share (say 10-20%, a subject to numerical optimization based on stakers' shares and behavior) of the total TrueFiStrategy holdings in a liquid form in order to reduce the need of big liquidity removals to reduce the cumulative TrueFiPool2's exit fees for Sherlock stakers.

Also, manual liquidExit() calls can be performed as private transactions.
