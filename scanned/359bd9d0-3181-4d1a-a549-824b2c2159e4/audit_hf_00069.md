# [C] GMXC-1 | Liquidations Prevented By Request Expiration

## Summary
Severity: Critical
Contest weight: 0.2134
Dataset id: 145
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidation, if a user has an open order, the order is cancelled in order to retrieve the underlying tokens. However orders cannot be cancelled while within the REQUEST_EXPIRATION_BLOCK_AGE. Therefore a malicious user can front-run liquidations and create an order to prevent liquidations. The REQUEST_EXPIRATION_BLOCK_AGE is currently configured to 1200 blocks on Arbitrum. In practice, the time to execute an order in GMX should be ~2 seconds, however when the deposit or withdrawal feature is disabled on GMX the keeper will not execute or cancel orders. Therefore a malicious user can gain a ~5 minute grace period where they cannot be liquidated due to the REQUEST_EXPIRATION_BLOCK_AGE when the deposit or withdrawal feature is disabled as the order will not be executed or cancelled by the keeper.

## Recommendation
Do not allow the creation of orders when an account is liquidatable. Additionally, consider validating that the deposit and withdrawal feature are enabled before users are able to use the ACTION_CREATE_ORDER.
