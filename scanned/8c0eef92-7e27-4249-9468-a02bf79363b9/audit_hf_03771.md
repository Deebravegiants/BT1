# [H] CollateralManager#commitCollateral can be

## Summary
Severity: High
Contest weight: 0.7856
Dataset id: 19944
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
CollateralManager#commitCollateral never checks if the loan has been accepted
allowing users to add collaterals after which can DOS the loan.
CollateralManager.sol#L117-L130
function commitCollateral(
uint256 _bidId,
Collateral[] calldata _collateralInfo
) public returns (bool validation_) {
address borrower = tellerV2.getLoanBorrower(_bidId);
never checks that loan isn't active
if (validation_) {
for (uint256 i; i < _collateralInfo.length; i++) {
Collateral memory info = _collateralInfo[i];
_commitCollateral(_bidId, info);
}
}
}
CollateralManager#commitCollateral does not contain any check that the bidId is
pending or at least that it isn't accepted. This means that collateral can be
committed to an already accepted bid, modifying bidCollaterals.
kages/contracts/contracts/CollateralManager.sol#L393-L409
function _withdraw(uint256 _bidId, address _receiver) internal virtual {
for (
uint256 i;
i < _bidCollaterals[_bidId].collateralAddresses.length();
i++
) {
// Get collateral info
Collateral storage collateralInfo = _bidCollaterals[_bidId]
.collateralInfo[
_bidCollaterals[_bidId].collateralAddresses.at(i)
];
// Withdraw collateral from escrow and send it to bid lender
ICollateralEscrowV1(_escrows[_bidId]).withdraw(
collateralInfo._collateralAddress,
collateralInfo._amount,
_receiver
);
bidCollaterals is used to trigger the withdrawal from the escrow to the receiver,
which closing the loan and liquidations. This can be used to DOS a loan AFTER it
has already been filled.
1) User A creates a bid for 10 ETH against 50,000 USDC at 10% APR
2) User B sees this bid and decides to fill it
3) After the loan is accepted, User A calls CollateralManager#commitCollateral
with a malicious token they create
4) User A doesn't pay their loan and it becomes liquidatable
5) User B calls liquidate but it reverts when the escrow attempts to transfer out
the malicious token
6) User A demands a ransom to return the funds
7) User A enables the malicious token transfer once the ransom is paid
Loans can be permanently DOS'd even after being accepted
```

## Recommendation
```solidity
CollateralManager#commitCollateral should revert if loan is active.
```
