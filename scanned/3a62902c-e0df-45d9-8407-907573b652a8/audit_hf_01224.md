# [H] Morpho rewards cannot be claimed due to ﬂawed integration with rewards distributor

## Summary
Severity: High
Contest weight: 0.1889
Dataset id: 5493
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The claimRewardsForToken function of the MorphoVaultRouter contract is intended for the admin to claim token rewards from Morpho's rewards distributor. To do this, the function ﬁrst intends to call IMorphoRewardDistributor::claim and then transfer the received tokens to a receiver account passed as parameter by the admin. However, the ﬁrst argument passed to claim is msg.sender - that is, the admin's account. As a consequence, the MorphoVaultRouter never receives the tokens from the distributor, and the token transfer after the call to claim will inevitably fail. Thus breaking the whole claiming process.

## Recommendation
Modify the claimRewardsForToken function so that it correctly integrates with Morpho's rewards distributor contract, ensuring that the MorphoVaultRouter contract is the one receiving the rewards before transferring them to the intended receiver account. Also, consider improving the integration tests to ensure this integration with Morpho's contract works as intended.
