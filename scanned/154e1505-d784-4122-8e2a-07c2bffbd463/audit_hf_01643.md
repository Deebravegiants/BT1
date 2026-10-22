# [H] Incorrect fee calculation and token accounting in sellToken function

## Summary
Severity: High
Contest weight: 0.2692
Dataset id: 8794
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The sellToken function in the HotCurves contract is designed to facilitate the sale of tokens by users, applying fees and distributing them to a referrer and a designated fee address. However, the current implementation contains a flaw in the fee calculation and token accounting logic. The function incorrectly computes the conversion from tokens to ETH multiple times: once for the referrer fee, once for the fee address, and once for the remaining token amount. This repeated conversion over the same portion of the curve leads to inflated ETH amounts being calculated and distributed, resulting in financial discrepancies. Additionally, the virtualTokenLp is only increased by the portion of tokens not related to the fees, which is incorrect. The entire _amount of tokens should be accounted for in the liquidity pool, as all tokens are effectively entering the pool. Similarly, virtualEthLp and realEthLp are only decreased by the eth amount unrelated to the fees, which is also incorrect.

## Recommendation
To resolve these issues, the function should first compute the total ETH equivalent of the _amount using the ethAmount function, obtaining _ethAmount. The fees should then be calculated as a proportion of _ethAmount. The ETH portion related to the fees should be distributed to the referrer and the fee address, while the remaining ETH should be sent to the msg.sender. Furthermore, ensure that virtualTokenLp is increased by the full _amount to accurately reflect the total tokens entering the pool, and that both virtualEthLp and realEthLp are decreased by _ethAmount.
