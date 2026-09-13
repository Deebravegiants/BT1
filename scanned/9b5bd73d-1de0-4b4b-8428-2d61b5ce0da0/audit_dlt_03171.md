# [M] Mitigation of M-12: Issue NOT mitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/66
Type: code-finding

## Details
## Mitigated issue
[M-12: No slippage protection on stake() in SafEth.sol](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/150)

There were issues with either a lack of slippage protection or a hard set slippage.
Slippage protection was missing in `deposit()` (for `Reth.deposit()` only if depositing in the Rocket Pool) and in `Reth.withdraw()`, as well as in `stake()` because of `ethPerDerivative()`.
Slippage was hard set in `Reth.deposit()` (only if via Uniswap), `SfrxEth.withdraw()` and `WstEth.withdraw()`.

## Mitigation review
`stake()` and `unstake()` now takes a `_minOut` parameter which the amount of safETH or ETH returned is compared. This mitigates the issue with a lack of slippage protection to prevent the user from losing funds.

The hard slippage settable only by the owner remains [in `Reth.deposit()`](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/derivatives/Reth.sol#L151-L152) (for all deposits now), [in `SfrxEth.withdraw()`](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/derivatives/SfrxEth.sol#L90-L91) and [in `WstEth.withdraw()`](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/derivatives/WstEth.sol#L75).

`Reth.deposit()` now only has one path to RocketSwapRouter, so this hard slippage always applies.

Furthermore, a hard slippage has now also been introduced [in `Reth.withdraw()`](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/derivatives/Reth.sol#L121). Therefore this is a new issue, reported under the title "Hard slippage in Reth.withdraw()".

## Recommendation
Remove all slippage control from the derivatives and control slippage only in `SafEth.stake()` and `SafEth.unstake()` with the new `_minOut`.

Note that this enables an attacker to cause a stake distribution different from the one given by the weights. This would be achieved by manipulating two exchanges such that the sum returned from `stake()` is within the slippage tolerance but such that the individual slippage in each exchange is great, positive in one, negative in the other. However, I'm not sure how anyone could benefit from this. Maybe it could be exploited to target a pool to deplete it, leveraging Asymmetry to do so.
To prevent this a distribution slippage would be needed, which sets a slippage for each derivative individually (as is/was almost the case). These slippages would then also have to be provided by the user.
