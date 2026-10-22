# [M] M-1 The owner is able to withdraw pool share tokens from speciﬁc adapters

## Summary
Severity: Medium
Contest weight: 0.1113
Dataset id: 10715
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A centralization concern has emerged within the AaveV3Adapter, WrappedCETHAdapter, and MA3WETHAdapter contracts. These adapters, inheriting from the ERC-20 tokens, serve as target tokens assigned to Tranche. Contrarily, the adapters maintain on their balance the pool shares from connected protocols, into which the target tokens are converted. This architecture leads to a possibility inherited from the BaseAdapter logic, where the owner might have the capability to withdraw these pool shares from the adapters. This issue is rated as medium severity as such a withdrawal could potentially disrupt the logic and ﬁnancial stability of the speciﬁed adapters, but may be triggered only by the authorized account (owner).

## Recommendation
We recommend disabling the redemption of pool shares from the speciﬁed adapters.
