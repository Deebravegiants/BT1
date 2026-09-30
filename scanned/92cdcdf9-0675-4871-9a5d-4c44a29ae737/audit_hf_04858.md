# [M] Wrong slippage protection

## Summary
Severity: Medium
Contest weight: 0.1949
Dataset id: 22757
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In distributePremium() there is a slippage protection which calculates minimum expected tokens for the bondTo() function. First it pulls the estimated amount of tokens from the FSD contract and then multiply it by the slippageTolerance variable. Both parts of the calculation don't work correctly which makes the slippage protection ineffective. 2/contracts/network/FairSideNetwork.sol#L539-L544 First lets look at the implementation of the estimateMintAmount function. As an argument it takes the membership fee in ethers. 2/contracts/token/FSD.sol#L358-L360 The first argument of the calculateDeltaOfFSD() function is getReserveBalance() - ethAmount, where getReserveBalance is the total ethereum amount owned by the FSD contract. The problem is that ethAmount is being subtracted from it which is not correct and only makes sense if the ethAmount is already transferred to the contract. But this is not the case because the eth amount is still in the FairSideNetwork contract. Secondly the initial value of the slippageTolerance is This is not correct because with the current implementation the token minimum amount would be 1% of the estimated amount but it should be 99% of it. I assume that this is not a big problem because the governance can set correct value using the setSlippageTolerance function. However it is behind a timelock and it will take at least 2 days to update it. Bad implementation of slippage protection

## Recommendation
Fix the estimateMintAmount function to not subtract the eth value from the total reserve and update the initial value of the slippageTolerance variable.
