# [H] H-14 | DoS In _withdrawFromPools Based On Util Ratio

## Summary
Severity: High
Contest weight: 0.2090
Dataset id: 2529
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _withdrawFromPools function uses the getAssetsOf function of the given BasePool to calculate the maximum that can be withdrawn. But the getAssetsOf function returns the amount that the SuperPool owns in the BasePool, not the amount that the SuperPool can withdraw right now.
This can lead to reverts and using the queue in a suboptimal way:
• The SuperPool has 100 tokens in the BasePool
• The user tries to withdraw 15 tokens
• The util ratio of the BasePool is 95% (Only 10 tokens can be withdrawn right now as the rest is borrowed)
• Therefore the SuperPool could withdraw 10 tokens from this pool and 5 tokens from the next one
• Instead, it tries to withdraw 15 tokens from this pool, the call fails and it will try to withdraw 15 from the next one
• This reorders the queue in a suboptimal way

## Recommendation
Reduce the borrowed funds from the assetsInPool, or set the assetsInPool to the balance of the BasePool if it's smaller. Do not withdraw more than available liquidity.
