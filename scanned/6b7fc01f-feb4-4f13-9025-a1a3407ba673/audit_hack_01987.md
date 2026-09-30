# [C] 6.1 Unchecked VaultManager Address

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

The fetchSurplusFromVaultManagers function is an external function of the contract
treasury/Treasury.sol, as displayed below, there is no check towards the user input
VaultManager address. An adversary can deploy a contract with a function
accrueInterestToTreasury which can return arbitrary numbers to maliciously update the state
variables surplusBufferValue and badDebtValue.


```
function fetchSurplusFromVaultManagers(address[] memory vaultManagers) external returns (uint256, uint256) {
(uint256 surplusBufferValue, uint256 badDebtValue) = _fetchSurplusFromList(vaultManagers);
return _updateSurplusAndBadDebt(surplusBufferValue, badDebtValue);
}
function _fetchSurplusFromList(address[] memory vaultManagers) internal returns (uint256 surplusBufferValue, uint256 badDebtValue) {
badDebtValue = badDebt;
surplusBufferValue = surplusBuffer;
uint256 newSurplus;
uint256 newBadDebt;
for (uint256 i = 0; i < vaultManagers.length; i++) {
(newSurplus, newBadDebt) = IVaultManager(vaultManagers[i]).accrueInterestToTreasury();
surplusBufferValue += newSurplus;
badDebtValue += newBadDebt;
}
}
```
Code corrected:

The vulnerable function fetchSurplusFromVaultManagers has been removed from the updated
code. Hence, the functionality to collect the surplus only from a subset of vault managers is not available
anymore. In order to collect the surplus accrued by all VaultManager contracts, function
fetchSurplusFromAll should be called.
