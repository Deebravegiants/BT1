# [M] MarginAccountHelper will be bricked if reg-

## Summary
Severity: Medium
Contest weight: 0.4009
Dataset id: 20117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
MarginAccountHelper#syncDeps causes the contract to refresh it's references to both marginAccount and insuranceFund. The issue is that approvals are never made to the new contracts rendering them useless.  
MarginAccountHelper.sol#L82-L87  
```solidity
function syncDeps(address _registry) public onlyGovernance {
    IRegistry registry = IRegistry(_registry);
    vusd = IVUSD(registry.vusd());
    marginAccount = IMarginAccount(registry.marginAccount());
    insuranceFund = IInsuranceFund(registry.insuranceFund());
}
```
When syncDeps is called the marginAccount and insuranceFund references are updated. All transactions require approvals to one of those two contract. Since no new approvals are made, the contract will become bricked and all transactions will revert.  
Contract will become bricked and all contracts that are integrated or depend on it will also be bricked

## Recommendation
Remove approvals to old contracts before changing and approve new contracts after
