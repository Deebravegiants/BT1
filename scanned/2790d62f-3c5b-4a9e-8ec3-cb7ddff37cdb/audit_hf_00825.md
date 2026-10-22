# [H] H-04 | Debt Burden After Vault Liquidation

## Summary
Severity: High
Contest weight: 0.3311
Dataset id: 2561
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Vault liquidations are quite profitable for the liquidator who pays back the V3 debt but receives all collateral in the vault. As migrateOnBehalf can be called by anyone, an attacker may be able to put the SNX vault in a liquidatable state by migrating the right positions from V2, which would result in the c-ratio of the vault dropping below the collateralConfig.liquidationRatioD18 and become open for vault liquidation. This would be especially possible if only a handful of small accounts were migrated to V3, and then a big liquidatable account is force migrated to make the entire vault liquidatable. In the event of a vault liquidation, all debts are settled and the liquidator takes all collateral from the vault. Assuming there is only one vault in the pool, then there would be no collateral backing the debt shares that the Legacy market holds. This state in itself is somewhat peculiar and should be examined further. One concern would be during the period after vault liquidation till the next time another user migrate. If debt shares increase in value during that period, then the next user to migrate take on all extra debt. In many cases, any subsequent migrators/delegators would become immediately liquidatable by unfairly taking on debt that did not belong to them.

## Proof of Concept
https://github.com/GuardianAudits/legacy-1/pull/6/commits/532e5b06bb0137c8b44c8751e51b90d567535387#diff-3d7ac216cfd17a1907d878223ef7603f69889d7911d6049a1a9e2b9444604722R272

## Recommendation
Ensure sufficient volume of healthy accounts are migrated first to ensure that vault liquidation is very unlikely to happen. Also, consider handling the scenario after vault liquidation where the pool goes out of range for a market, and do not attribute any increase in debt to the next user that migrates.
