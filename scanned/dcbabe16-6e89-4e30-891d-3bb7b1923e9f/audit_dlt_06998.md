# [M] Wrong slippage check

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-redacted-cartel
Published: 2022-02-16
Source: https://github.com/code-423n4/2022-02-redacted-cartel-findings/issues/35
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-redacted-cartel/blob/92c4d5810df7b9de15eae55dc7641c8b36cd799d/contracts/ThecosomataETH.sol#L115


# Vulnerability details

## Impact
The `ThecosomataETH.addLiquidity` function computes the `expectedAmount` and then subtracts a slippage percentage from it.


```solidity
function addLiquidity(uint256 ethAmount, uint256 btrflyAmount) internal {
    uint256[2] memory amounts = [ethAmount, btrflyAmount];
    uint256 expectedAmount = ICurveCryptoPool(CURVEPOOL).calc_token_amount(
        amounts
    );
    uint256 minAmount = expectedAmount - ((expectedAmount * slippage) / 1000);

    ICurveCryptoPool(CURVEPOOL).add_liquidity(amounts, minAmount);
}
```

According to the [Curve docs 21.4](https://curve.readthedocs.io/_/downloads/en/latest/pdf/), this amount is already exact and takes the slippage into account (but not fees).

If the pool is imbalanced, the `calc_token_amount` will already return a wrong amount and the additional slippage check on the wrong amount is unnecessary (except for the fees).

## Recommended Mitigation Steps
Consider computing the minimum expected LP tokens off-chain and pass them to the `performUpkeep` function as a parameter to prevent sandwich attacks.
