# [C] C-2 Battle fishing attack

## Summary
Severity: Critical
Contest weight: 0.1572
Dataset id: 7524
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Arena smart contract contains a public Arena.sol#L67 function that creates a new battle without initializing. This function is used in the BattleInitializer's function BattleInitializer.sol#L14. It means that an attacker can create a new battle and binds it to a fake manager behind the scene. Using the manager privilege, the fake manager contract can mint spear and shield tokens and put them to the pool. A user will trade these tokens for collateral. At the end of the battle the attacker could withdraw assets using the Battle.sol#L271 function of the battle.

## Recommendation
We recommend improving the access right model to disallow attackers to gain privileged access.
