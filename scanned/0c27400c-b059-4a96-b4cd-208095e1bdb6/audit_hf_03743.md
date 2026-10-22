# [M] Adversary can break NFT distribution by de-

## Summary
Severity: Medium
Contest weight: 0.0917
Dataset id: 19886
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Bounties limit the number of NFT deposits to five. An adversary can block adding NFTs by repeatedly depositing and withdrawing an NFT.
plementations/BountyCore.sol#L64-L93
All bounties use BountyCore#refundDeposit to process refunds to user. This simply transfers the NFT back to the funder but leaves the nftDeposit. This uses up the deposit limit which is current set to 5. Since the deposit cap is used up by deposits that have been refunded the slots can't be used to distribute legitimate NFTs to the bounty claimant.
Adversary can block legitimate NFT distribution

## Recommendation
When an NFT deposit is refunded it should remove the depositID from nftDeposits
