# [H] H-05 | ADL Returns Native ETH

## Summary
Severity: High
Contest weight: 0.1848
Dataset id: 2037
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During auto deleveraging (ADL) scenarios, GMX keepers will automatically close positions. According to the docs, When the pending profits exceed the market's configured threshold, profitable positions may be partially or fully closed. The issue arises for the WETH vault, as ADL will return the remaining collateral in native ETH and not WETH. Therefore, the AggregateVault.getVaultPPS will have an invalid state as only WETH balance is accounted for, creating a big step wise jump, allowing users to deposit/withdraw with an incorrect share price calculation.

## Proof of Concept
https://github.com/GuardianAudits/umamipositionmanager-2/pull/4

## Recommendation
After an ADL scenario, GMX will close the position and execute afterOrderExecution callback. Consider validating if order.flags.shouldUnwrapNativeToken is true, and either pause or wrap the native tokens into WETH.
