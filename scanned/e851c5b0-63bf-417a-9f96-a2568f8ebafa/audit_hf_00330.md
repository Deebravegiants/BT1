# [M] Private sale spoofing

## Summary
Severity: Medium
Contest weight: 0.0988
Dataset id: 1608
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Similar to [spoofing in finance](https://en.wikipedia.org/wiki/Spoofing_\(finance\)), users can create private sales with correct signatures but then frontrun the buy with a transfer to a different wallet they control.

No funds are lost as the NFT <> FETH exchange is atomic but it can be bad if third parties create a naive off-chain centralized NFT market based on this signature feature.  
It’s also frustrating for the users if they try to accept the private sale but their transaction fails.

## Recommendation
This is made possible because private sales do not keep the NFT in escrow.  
Consider escrowing the NFT also for private sales.
We are actually considering moving private sales to an escrow system. But we’ll leave it as-is for now for backwards compatibility and to simplify our upcoming launch.

We understand this could happen and will update the comments to make that more clear.
