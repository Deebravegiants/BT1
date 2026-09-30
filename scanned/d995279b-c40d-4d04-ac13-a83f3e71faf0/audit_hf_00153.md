# [M] Missleading `onlyDAO` modifiers

## Summary
Severity: Medium
Contest weight: 0.1769
Dataset id: 725
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Several contracts implement an `onlyDAO` modifier which, as the name suggests, should only authorize the function to be executed by the DAO. However, some implementations are wrong and either allow the DAO or the deployer to execute, or even only the deployer:

Incorrect implementations:

* `BondVault.onlyDAO`: allows deployer + DAO
* `DAO.onlyDAO`: allows deployer
* `DAOVault.onlyDAO`: allows deployer + DAO
* `poolFactory.onlyDAO`: allows deployer + DAO
* `Router.onlyDAO`: allows deployer + DAO
* `Synth.onlyDAO`: allows deployer
* `synthFactory.onlyDAO`: allows deployer
* `synthVault.onlyDAO`: allows deployer + DAO

In all of these functions, the deployer may execute the function as well which is a centralization risk. The deployer can only sometimes be purged, as in `synthFactory`, in which case nobody can execute these functions anymore.

Recommend renaming it to `onlyDeployer` or `onlyDeployerOrDAO` depending on who has access.

This is by design a choice. However, there are current discussions around renaming the high level access modifiers to be more descriptive in their purpose.

This is a non-critical issue because there’s no in-code bugs, it’s rather error-prone naming.

On second look, I’ll keep it a medium risk as deployer cannot be purged in all contracts which introduces systemic risk.

## Recommendation
No recommendation
