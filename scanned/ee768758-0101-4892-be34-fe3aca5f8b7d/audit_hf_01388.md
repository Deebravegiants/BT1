# [M] M-4 TwoWayLendingFactory price manipulation

## Summary
Severity: Medium
Contest weight: 0.0933
Dataset id: 7118
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• CryptoFromPoolVault.vy#L65
• OracleVaultWrapper.vy#L39
These oracles are used in TwoWayLendingFactory. If you try to inﬂuence the price via controllerlong/controllershort, there will be a check_lock check (Vault.vy#L266). However, an attacker still has the ability to inﬂuence the price via a transfer to the controller. For example:
print(ammshort.priceoracle()) # 1000000000000000
borrowedtoken.transfer(controllerlong, amount)
print(ammshort.priceoracle()) # 1250000000000000
This can be advantageous if there are few funds in the Controller and it is very easy to inﬂuence the price.

## Recommendation
We recommend using a more stable oracle to price the LP Vault.
