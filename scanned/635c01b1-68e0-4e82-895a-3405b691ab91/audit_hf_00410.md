# [M] Upgradability of Token Bridge

## Summary
Severity: Medium
Contest weight: 0.1453
Dataset id: 1812
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The TokenBridge address will change when migrating from Hyperlane to Superchain. As a result, external integrators might not be able to bridge XVELO.
It is announced that Velodrome will migrate from Hyperlane to Superchain in the future.
However, the TokenBridge is immutable and not upgradable. As a result, to facilitate the migration from Hyperlane to Superchain, a new TokenBridge contract with the new Superchain's logic has to be deployed, which will inevitably lead to a new bridge address.
As a result, external protocols that integrate with the TokenBridge and hardcode the bridge address OR the external protocol itself is immutable will encounter issues when the bridge address changes.
External integrators might not be able to bridge XVELO if the TokenBridge address changes due to migration to the Superchain bridge and the older Hyperplane's token bridge has been decommissioned.

## Recommendation
Consider any of the following mitigation actions:
1. Update the TokenBridge to be upgradable so that the bridge logic can be updated without changing the bridge address
2. Consider documenting that the token bridge address will change when migrating from Hyperlane to Superchain in the future so that the integrators are aware of this.
