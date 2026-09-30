# [H] H-01 | Users Incorrectly Credited WIth NFT Ownership At lzReceive Time

## Summary
Severity: High
Contest weight: 0.2819
Dataset id: 1999
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _claimBatch function after the claim has been validated by the l1 state at the timestamp of the requestClaim call, the claimer is awarded with the vested amount computed by the _vested function. However the _vested function determines the user’s vested amount based upon the current block.timestamp of the lzReceive action. This is however not the same timestamp that the claimer was veriﬁed to be authorized to claim at. The claimer could have sold their NFT to another user after the block.timestamp of the requestClaim call and thus received vested amounts which should have gone to the new owner of the NFT. There is a 8 block confirmation threshold currently conﬁgured, meaning that roughly 96 seconds will have to occur at minimum between the requestClaim call and the lzReceive which fulﬁlls the claim. This delay period could be made even more severe during a DVN outage or if a claim has passed all DVN checks but the lzReceive function reverts for some time until the revert is resolved (e.g. claim contract is paused and unpaused, or the daily withdrawal threshold has been met for the day) and then the lzReceive function is invoked again successfully passing a significant amount of time later.

## Recommendation
Include the timestamp of the claim request in the ClaimParameters for the corresponding claimNonce if the claimer is shown to be validated for all of the claims then the claims should be carried out up to the stored timestamp of the claim request.
