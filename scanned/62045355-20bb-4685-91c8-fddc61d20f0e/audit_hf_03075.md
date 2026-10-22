# [H] Bank run is possible when the product is insolvent.

## Summary
Severity: High
Contest weight: 0.3069
Dataset id: 17373
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a product becomes insolvent, the last user(s) will not be able to withdraw their full balance. When one or more accounts go bankrupt, the bad debt will be accumulated in the product as the shortfall. When shortfall > 0 it means the product is now insolvent i.e. the total assets (product.total) is lower than the total liabilities (sum of all takers and makers' product accounts). If a protocol becomes insolvent, the protocol owner (or a backer e.g. re-insurance fund) has the responsibility to resolve the shortfall, but there is nothing in the protocol to guarantee the protocol’s shortfall to be resolved in time for all users’ withdrawals to be made whole. Furthermore, when a user withdraws, the product’s shortfall is not taken into consideration. Early withdrawals will be able to close their position without being impacted by the insolvency but the protocol may not have sufficient funds for later withdrawals of the insolvent product. Therefore early users can be made whole as there are still enough assets for them to exit, but late users or at least the last user will not be able to withdraw their entire balance. This will make the users of the insolvent product rush to withdraw their balances, i.e. a bank run scenario.

## Recommendation
Withdrawals in insolvent products should account for any shortfall in proportion to their account’s open positions. The shortfall should be reflected in the OptimisticLedger of the product, and the frozenBalance will be settled for the shortfall accumulated and resolved in the account settlement flywheel. We believe it's better if the shortfall accumulated and resolved is based on per unit of open position instead of per unit of collateral, because a user with some balance in the product but no open position should not bear the negative impact from any shortfall caused by bankrupt accounts.
