# [M] Missleading onlyDAO modifiers

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

cmichel


# Vulnerability details

Several contracts implement an `onlyDAO` modifier which, as the name suggests, should only authorize the function to be executed by the DAO.
However, some implementations are wrong and either allow the DAO or the deployer to execute, or even only the deployer:

Incorrect implementations:
- `BondVault.onlyDAO`: allows deployer + DAO
- `DAO.onlyDAO`: allows deployer
- `DAOVault.onlyDAO`: allows deployer + DAO
- `poolFactory.onlyDAO`: allows deployer + DAO
- `Router.onlyDAO`: allows deployer + DAO
- `Synth.onlyDAO`: allows deployer
- `synthFactory.onlyDAO`: allows deployer
- `synthVault.onlyDAO`: allows deployer + DAO

## Impact
In all of these functions, the deployer may execute the function as well which is a centralization risk.
The deployer can only sometimes be purged, as in `synthFactory`, in which case nobody can execute these functions anymore.

## Recommended Mitigation Steps
Rename it to `onlyDeployer` or `onlyDeployerOrDAO` depending on who has access.
