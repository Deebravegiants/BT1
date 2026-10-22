# [M] Reclaiming asset will fail when the option writer is also the highest bidder.

## Summary
Severity: Medium
Contest weight: 0.2061
Dataset id: 17489
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Hook allows for the option writer to reclaim i.e. withdraw the underlying asset from an active option if certain conditions are met. However, this will fail if the option writer is also the highest bidder.
Protocol documentation states that: “If the writer wishes to withdraw the underlying asset from an active option, they first must obtain the option instrument NFT and transfer it to the writer account. Then, they may call the reclaim function, which will release the entitlement on the vault, return any active bids to the bidder, and burn the option NFT. They may then either withdrawal the asset from the vault or mint a new option with it.”
However, the implementation does not account for the scenario where the option writer is also the highest bidder at the time of reclaiming. _returnBidToPreviousBidder and settleOption handle this scenario by subtracting the call strike amount during _safeTransferETHWithFallback to the option writer. This is because the option writer is allowed to bid by only paying the difference between their bid and strike price.
Therefore, if call.writer is also the call.highBidder at the time of attempting to reclaim then _safeTransferETHWithFallback(call.highBidder, call.bid) will revert because the option contract will only have ETH amount equal to the spread but not the strike part of call.bid.
Option writer is unable to reclaim the underlying asset in the scenario when the writer is also the highest bidder.

## Recommendation
Check if the highest bidder is the option writer during reclaiming and pay back only the spread amount in that scenario instead of call.bid which includes both the strike and spread parts.
Return the correct amount of eth (high bid - strike) to high bidder during reclaim when high bidder is call writer.
https://github.com/hookart/protocol/pull/64
Ok.
