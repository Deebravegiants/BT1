# [M] TrueFi can't liquidExit if there isn't enough liquidity remaining

## Summary
Severity: Medium
Reporter: Chom
Source: https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L498
Type: audit-issue

## Details
# TrueFi can't liquidExit if there isn't enough liquidity remaining

## Summary
TrueFi can't liquidExit if there isn't enough liquidity remaining

## Vulnerability Detail

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L498

TrueFi liquid exit only works if there is enough liquidity due to ensureSufficientLiquidity checks.

```solidity
ensureSufficientLiquidity(amountToWithdraw);
...
    function ensureSufficientLiquidity(uint256 neededAmount) internal {
        uint256 currentlyAvailableAmount = currencyBalance();
        if (currentlyAvailableAmount < neededAmount) {
            require(address(strategy) != address(0), "TrueFiPool: Pool has no strategy to withdraw from");
            strategy.withdraw(neededAmount.sub(currentlyAvailableAmount));
            require(currencyBalance() >= neededAmount, "TrueFiPool: Not enough funds taken from the strategy");
        }
    }
```

## Impact
You may not able to withdraw a large chunk of funds. In case you need immediate USDC liquidity in situations such as panic withdraw or the enormous protocol claiming.

## Code Snippet

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L498

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L436-L443

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L155-L185

## Tool used

Manual Review

## Recommendation
No solution if you want to use TrueFi
