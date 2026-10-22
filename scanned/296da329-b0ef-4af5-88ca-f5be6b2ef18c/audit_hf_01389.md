# [M] M-5 AggregateStablePrice EMA can be manipulated

## Summary
Severity: Medium
Contest weight: 0.1432
Dataset id: 7119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• AggregateStablePrice2.vy#L167-L168
If the pricew() function, which updates lasttimestamp, is not called for a long time, the value of alpha decreases, leading to a risk of EMA manipulation by a hacker. This occurs because the closer alpha gets to zero, the greater the inﬂuence of the new totalSupply() value, which can be manipulated within the current transaction:
alpha: uint256 = 10**18
if last_timestamp < block.timestamp:
alpha = self.exp(- convert((block.timestamp - last_timestamp) * 10**18 / TVLMATIME, int256))
...
if alpha != 10**18:
alpha = 1.0 when dt = 0
alpha = 0.0 when dt = inf
newtvl: uint256 = self.pricepairs[i].pool.totalSupply()
tvl = (new_tvl * (10**18 - alpha) + tvl * alpha) / 10**18
For example, after 10 * TVLMATIME seconds (which is about 5 days in the current implementation), if no one calls the function, alpha becomes 0.0000453999. Ultimately, if alpha=0, new_tvl will simply be equal to totalSupply().

## Recommendation
We recommend considering the possibility of manipulation with this aggregator and, for example, implementing monitoring to check if the price_w() function has not been called for a long time.
