# [C] DIEMT-1 | DeltaT Rounds Down To 0 Bricking Trades

## Summary
Severity: Critical
Contest weight: 0.2587
Dataset id: 100
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
secondsToExpiry is divided by 15 to produce deltaT. Options with <15 seconds of expiry will have deltaT rounded down to 0 and will cause functions such as calculateCosts(), interestRate() and utilizationRatio() to revert. The above functions call Binomial._optionPrices which calculates N period for binomial pricing: uint256 N = inputs.secondsToExpiry / inputs.deltaT; Because inputs.deltaT is 0 after rounding down, a division by 0 revert occurs. While the option is included in the activeOptionIds, all other options will be impacted: interestRate() and calculateCosts() are needed for pnlOperations, which will completely prevent closing and liquidation trades from occurring due to the revert. This will negatively impact liquidity providers and traders. calculateCosts() and utilizationRatio() are called when opening a trade, completely preventing trades from being opened in the protocol.

## Proof of Concept
https://github.com/GuardianAudits/IVX-Suite/blob/67b520e0ec04b8c4403a0f235199a7e0b1d6e36b/test/pocs/RoundingDownExpiry.t.sol#L46

## Recommendation
Use the default inputs.deltaT value to prevent N from becoming 0. Furthermore, carefully monitor expired options and ensure they are settled to prevent bloating the active options list.
