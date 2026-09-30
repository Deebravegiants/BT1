# [M] M-09 | vEth Credited When Closing A Position

## Summary
Severity: Medium
Contest weight: 0.1335
Dataset id: 1976
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When closing a position, the vEthToZero is calculated as initialSize * tradeRatio and should be equal to the signedTradedVEth. However, Solidity division truncates the result. Because of this, tradeRatio will be slightly off - both when rounded down or up - therefore vEthToZero as well. Even though vEthFromZero should be roughly equal to targetSize * tradeRatio, the value assigned to it (for targetSize = 0) will be non-zero - positive or negative depending on the rounding. After that the absolute value of vEthFromZero will be assigned to vEthAmount. In result, closed positions end up having positive vEthAmount, which is especially bad for long positions. This ultimately leads to an undercollateralized market, preventing the last user from settling.

## Proof of Concept
https://github.com/GuardianAudits/foil-fuzzing/commit/c6d9b52b12a46e0a52f31ef28ecf343980b9ec01

## Recommendation
Consider setting the vEthAmount of the new position to 0, if its size is 0 as well.
