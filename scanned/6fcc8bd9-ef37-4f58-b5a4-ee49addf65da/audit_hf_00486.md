# [M] Repayer can brick lending func-

## Summary
Severity: Medium
Contest weight: 0.5925
Dataset id: 1928
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LenderCommitmentGroup_Smart doesn't handle excess repayments making it possible to brick the lending functionality
The function performs totalPrincipalTokensLended-totalPrincipalTokensRepaid without handling the underflow scenario. This is problematic as excess amount can be repaid for loans which will cause an underflow here
```solidity
function getTotalPrincipalTokensOutstandingInActiveLoans() public view returns (uint256) {
    return totalPrincipalTokensLended - totalPrincipalTokensRepaid;
}
```
on excess repayments, totalPrincipalTokensRepaid will become greater than totalPrinc ipalTokensLended
```solidity
function repayLoanCallback(
    uint256 _bidId,
    address repayer,
    uint256 principalAmount,
    uint256 interestAmount
) external onlyTellerV2 whenForwarderNotPaused whenNotPaused bidIsActiveForGroup(_bidId) {
    totalPrincipalTokensRepaid += principalAmount;
    totalInterestCollected += interestAmount;
}
```
function in TellerV2.sol contract to repay excess amount. User can specify any amount greater than minimum amount
```solidity
function repayLoan(uint256 _bidId, uint256 _amount) external acceptedLoan(_bidId, "rl") {
    _repayLoanAtleastMinimum(_bidId, _amount, true);
}
```
The function getTotalPrincipalTokensOutstandingInActiveLoans is invoked before every lending. Hence an underflow here will cause the lending functionality to revert
Another quirk regarding excess repayments is that the lenders of the pool won't obtain the excess repaid amount since it is not accounted anywhere. But this cannot be considered an issue since the lenders are only guarenteed the original lending amount + interest
Internal pre-conditions
External pre-conditions
Attack Path
1. Attacker borrows 100 from the lender pool totalPrincipalTokensLended == 100 totalPrincipalTokensRepaid == 0
2. Attacker repays 101 totalPrincipalTokensLended == 100 totalPrincipalTokensRepaid == 101
Now getTotalPrincipalTokensOutstandingInActiveLoans will always revert
Bricked lending functionality

## Recommendation
In case repaid principal is more, return 0 instead
