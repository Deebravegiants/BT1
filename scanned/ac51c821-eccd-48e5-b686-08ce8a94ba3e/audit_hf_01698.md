# [M] A user could evade acquiring interest on his debt

## Summary
Severity: Medium
Contest weight: 0.2575
Dataset id: 9309
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users create vaults where they store collateral and mint the protocol's stable coin in return. The amount of stable coin minted is defined as debt. The debt minted acquires interest over time which calculated in the VaultOperations::calculateAccruedInterest function and is time dependent. The lastDebtUpdateTime mapping is used to store the last timestamp interest was acquired. The only place where the function is called in from the manageDebtInterest() function, where if the lastDebtUpdateTime is zero, it is set to block.timestamp and no interest is accrued.  
=> uint256 lastUpdated = lastDebtUpdateTime[_vaultOwner][_vaultCollateral]; // load last update debt time  
uint256 currentTimestamp = block.timestamp; // ok  
if (lastUpdated == 0 || lastUpdated >= currentTimestamp || debtAmount == 0) {  
=> lastDebtUpdateTime[_vaultOwner][_vaultCollateral] = currentTimestamp;  
return (collateralAmount, debtAmount, vaultMCR);  
}  
uint256 vaultInterestRate = IVaultManager(vaultManager).getVaultInterestRate(_vaultCollateral, _vaultOwner);  
=> uint256 accruedInterest = calculateAccruedInterest(debtAmount, vaultInterestRate, lastUpdated, currentTimestamp);  
When a user is liquidated his lastDebtUpdateTime is set to 0. This is fine, but not if he is partially liquidated. If a user is partially liquidated his lastDebtUpdateTime will set 0 and stop accruing interest even if there is collateral and debt left. Also a user can self-liquidate. Having this in mind a malicious user could just lower his min CR and self liquidate just a little amount so his lastDebtUpdateTime is set to 0 and stop acquiring interest. In the same transaction he cal call adjustVault and add more collateral so someone else doesn't liquidate him. This way a malicious user could escape acquiring interest on his debt.

## Recommendation
In the VaultOperations::liquidateVault function set the lastDebtUpdateTime to zero only if it is full liquidation, otherwise set it to block.timestamp which done by default in manageDebtInterest.  
(uint256 collateralAmount, uint256 debtAmount, uint256 vaultMCR) = manageDebtInterest(vaultCollateral, vaultOwner);  
- lastDebtUpdateTime[vaultOwner][vaultCollateral] = 0;  
// Full liquidation  
if (debtToOffset == debtAmount) {  
+ lastDebtUpdateTime[vaultOwner][vaultCollateral] = 0;  
activeVaults -= 1;  
IVaultSorter(vaultSorter).removeVault(vaultCollateral, vaultOwner);  
IVaultManager(vaultManager).adjustVaultData(vaultCollateral, vaultOwner, 0, 0, 0);  
// Update total debt and collateral  
totalDebt[vaultCollateral] -= debtAmount;  
totalCollateral[vaultCollateral] -= collateralAmount;  
// Partial liquidation  
} else {
