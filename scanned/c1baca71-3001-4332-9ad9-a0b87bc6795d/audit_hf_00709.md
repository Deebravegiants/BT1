# [M] M-03 | Orders Can Be Censored By Front-running

## Summary
Severity: Medium
Contest weight: 0.1811
Dataset id: 2260
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Any one can control whether or not their order is settled by front-running keeper bots. A user may commit an Order A that has a very tight price limit in block 0. To prevent Order A from settling, in the same block 0, through a different account, they could also commit an Order B that would move the market slightly so that the slippage guard would prevent settlement of Order A. In the next block 1 they could pay higher gas on a call to settleOrder for Order B which would "disable" Order A. The keeper would notice that Order A was outside of price tolerance and during the next block would call cancelOrder. In anticipation of this, the user could, through yet another account, create an order to move the market back so that Order A could not be canceled. Back and forth they dance, until the user decides to let the order be canceled or settled. This ability to censor trades at-will would give the user an opportunity to perform risk-free trades. Proﬁt on a large risk-free trade could easily cover the gas for the multiple orders needed to manipulate the order's settleability.

## Proof of Concept
https://github.com/GuardianAudits/snx-bfp-1/blob/devtooligan-pocs/markets/bfp-market/test/integration/modules/guardian/poc/realizePnlTest.test.ts#L222-L366

## Recommendation
Consider restricting calls to settleOrder to only the Keepers and apply a random execution order.
