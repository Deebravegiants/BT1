# [H] No way to revert setInvestorLiquidateOnly

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23414
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setInvestorLiquidateOnly function in InvestorLockManagerBase.sol contains a logic error that prevents the disabling of liquidate-only mode once it has been enabled. The function includes a require statement that checks if the investor is already in liquidate-only mode and reverts if they are, making it impossible to toggle the state back to false.

```solidity
function setInvestorLiquidateOnly(string memory _investorId, bool _enabled) public
onlyTransferAgentOrAbove returns (bool) {
    require(!investorsLiquidateOnly[_investorId], "Investor is already in liquidate only mode");
    investorsLiquidateOnly[_investorId] = _enabled;
    emit InvestorLiquidateOnlySet(_investorId, _enabled);
    return true;
}
```

## Recommendation
Remove the require statement to allow toggling of the liquidate-only state.

```solidity
function setInvestorLiquidateOnly(string memory _investorId, bool _enabled) public
onlyTransferAgentOrAbove returns (bool) {
    // require(!investorsLiquidateOnly[_investorId], "Investor is already in liquidate only mode");
    investorsLiquidateOnly[_investorId] = _enabled;
    emit InvestorLiquidateOnlySet(_investorId, _enabled);
    return true;
}
```
