# [M] User can loseaccrued rewards during migration

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23338
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: User can migrate his staking position to new vault. However it will overwrite his rewardsAccrued in that new vault:
```solidity
function migrateToVault(address migrateTo)
external
onlyNotEmergencyMode
whenNotPaused
onlyTrustedCodehash
onlyRegisteredVault
{
if (vaultOwners[migrateTo] == address(0)) {
revert StakeManager__InvalidVault();
}
if (vaultData[migrateTo].stakedBalance > 0) {
revert StakeManager__MigrationTargetHasFunds();
}
_updateGlobalState();
_updateVault(msg.sender, false);
VaultData storage oldVault = vaultData[msg.sender];
VaultData storage newVault = vaultData[migrateTo];
// migrate vault data to new vault
newVault.stakedBalance = oldVault.stakedBalance;
newVault.rewardIndex = oldVault.rewardIndex;
newVault.mpAccrued = oldVault.mpAccrued;
newVault.maxMP = oldVault.maxMP;
newVault.lastMPUpdateTime = oldVault.lastMPUpdateTime;
@> newVault.rewardsAccrued = oldVault.rewardsAccrued;
IStakeVault.MigrationData memory migrationData = IStakeVault.MigrationData({
lockUntil: IStakeVault(msg.sender).lockUntil(),
depositedBalance: IStakeVault(msg.sender).depositedBalance()
});
IStakeVault(migrateTo).migrateFromVault(migrationData);
delete vaultData[msg.sender];
emit VaultMigrated(msg.sender, migrateTo);
}
```
Consider following example:
1) User has staking in old vault  
2) New vault version is released  
3) User creates stake in new vault  
4) Unstakes from new vault  
5) Migrates stake from old vault to the new one  
6) User loses unclaimed rewards in that new vault, which were earned between steps 3 and 4.  
Impact: User can lose accrued rewards during migration

## Recommendation
Recommended Mitigation: Ensure user migrates to empty vault:
```solidity
function migrateToVault(address migrateTo)
external
onlyNotEmergencyMode
whenNotPaused
onlyTrustedCodehash
onlyRegisteredVault
{
if (vaultOwners[migrateTo] == address(0)) {
revert StakeManager__InvalidVault();
}
- if (vaultData[migrateTo].stakedBalance > 0) {
+ if (vaultData[migrateTo].stakedBalance > 0 || vaultData[migrateTo].rewardsAccrued > 0) {
revert StakeManager__MigrationTargetHasFunds();
}
...
}
```
