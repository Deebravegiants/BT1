# [H] User can bypass copay and get 100% coverage

## Summary
Severity: High
Contest weight: 0.8926
Dataset id: 22759
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Users can open a "Cost Share Request" (CSR) using the FairSideClaim contract's
openPWPRequest. The function checks that the account has purchased enough cost
share benefits for the claim amount requested. However, the cross share benefit
is checked against claim amount after taking a 10 percent haircut. Therefore a user
can request availableCostShareBenefits * 10/9 to pass the check and get 100
percent coverage.
The following are the relevant snippets for the issue:
• Cost share requests are opened using the openPWPRequest function.
• requestPayout is returned after haircutting 10% of claimAmount in validateCSR
• The CostShareRequest takes the returned requestPayout as the claimAmount
(what will be paid)
uint256 private constant NON_USA = 0.9 ether;
function openPWPRequest(uint256 claimAmount, uint256 coverId, bool inETH)
external payable onlyCoverIdOwner(coverId) {
    (uint256 requestPayout, uint256 availableCostShareBenefits) =
    validateCSR(claimAmount, coverId);
    createCostshareRequest(requestPayout, claimAmount, 0, coverId);
}

function validateCSR(uint256 claimAmount, uint256 coverId) private view
returns (uint256, uint256) {
    Membership memory account = fairSideNetwork.getMembership(coverId);
    // 90% of the full claim is paid out as 10% in the USA
    uint256 requestPayout = claimAmount.mul(NON_USA);
    if (account.availableCostShareBenefits < requestPayout) {
        revert FSClaims_CostRequestExceedsAvailableCostShareBenefits();
    }
    return (requestPayout, account.availableCostShareBenefits);
}

function createCostshareRequest(uint256 requestPayout, uint256 claimAmount,
uint256 _csrType, uint256 coverId) private {
    CostShareRequest memory csr = CostShareRequest(
        uint80(block.timestamp),
        msg.sender,
        coverId,
        _csrType,
        requestPayout,
        bytes32(0),
        ClaimStatus.IN_PROGRESS
    );
    costShareRequests[nextClaimId] = csr;
}
```
As seen above, requestPayout is 90% of the claimAmount:
```solidity
uint256 requestPayout = claimAmount.mul(NON_USA);
```
Then the requestPayout is checked against the member's cost share benefits:
```solidity
if (account.availableCostShareBenefits < requestPayout) {
    revert FSClaims_CostRequestExceedsAvailableCostShareBenefits();
}
```
Therefore if the user passes a claimAmount that after 10% haircut will be equal to
availableCostShareBenefits and pass the if statement, then requestPayout will be
equal to the entire cost share benefit. User will receive 100% coverage.
The amount of claimAmount needed is availableCostShareBenefits * 10/9.
For example, if user purchased 90 ETH cost share benefits: 90 ether * 10/9 = 100
ether.
Supplying 100 ether as claimAmount will bypass the user copay.
Loss of funds. 100% coverage instead of expected 90%

## Recommendation
Consider changing the if statement to check against claimAmount instead:
```solidity
if (account.availableCostShareBenefits < claimAmount) {
    revert FSClaims_CostRequestExceedsAvailableCostShareBenefits();
}
```
