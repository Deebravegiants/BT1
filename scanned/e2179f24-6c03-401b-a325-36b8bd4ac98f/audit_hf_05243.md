# [H] stale issuance records after burn and seize operations

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23416
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The recordBurn() and recordSeize() functions in ComplianceServiceRegulated.sol do not clean up issuance records when tokens are burned or seized. This causes stale issuance records to persist in the system, which can lead to incorrect lock calculations for newly issued tokens. The cleanupInvestorIssuances() function only removes expired issuance records based on lock periods, but does not remove records for tokens that have been completely burned or seized.

```solidity
function recordBurn(address _who, uint256 _value) internal override returns (bool) {
    if (compareInvestorBalance(_who, _value, _value)) {
        adjustTotalInvestorsCounts(_who, CommonUtils.IncDec.Decrease);
    }
    return true;
}
```

Impact: Issuance records remain in the system for tokens that no longer exist. When an investor receives new tokens after a burn/seize operation, the lock calculation in getComplianceTransferableTokens() will include stale issuance records from the previously burned/seized tokens.

## Proof of Concept
1. Investor receives 100 tokens at timestamp T1 - Creates issuance record: `{value: 100, timestamp: T1}`
2. All 100 tokens are burned via burn() function  
   • `recordBurn()` is called but does NOT clean up issuance records  
   • Stale issuance record persists: `{value: 100, timestamp: T1}`
3. Investor receives 50 new tokens at timestamp T2 (after lock period)  
   • Creates new issuance record: `{value: 50, timestamp: T2}`
4. When calculating transferable tokens, `getComplianceTransferableTokens()` uses BOTH records:  
   • Stale record: 100 tokens from T1 (should not exist)  
   • New record: 50 tokens from T2
5. If lock period hasn't expired since T1, ALL 150 tokens are considered locked
6. Result: Investor cannot transfer any of their 50 new tokens due to stale lock calculation

## Recommendation
Delete the old issuance when a investor is complete burn or seize.
