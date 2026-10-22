# [H] withdrawNftWithInterest

## Summary
Severity: High
Contest weight: 0.7889
Dataset id: 18664
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the NFT withdrawal routine that is intended to let a lender reclaim an NFT after a loan has become inactive. The function checks only that the caller is the recorded lender and that the loan start timestamp is zero, then it deletes the lien record and transfers the NFT from the contract to the caller. Because the protocol does not enforce a one‑to‑one relationship between an NFT and a lien, multiple lien entries can reference the same token identifier. When a second user creates a new lien on an NFT that is already linked to an earlier lien, the contract stores both lien structures without any uniqueness guard. Consequently, if the original lender later invokes the withdrawal function for the first lien, the contract blindly deletes that lien and transfers the NFT that is currently held by the contract – which now belongs to the second lien holder – to the original caller. This allows the first lender to steal the NFT and any associated collateral from the second lender. The attack scenario unfolds as follows: (1) Alice deposits NFT_A and creates Lien[1]; (2) Bob sells NFT_A on a market; (3) Jack purchases NFT_A and creates Lien[2] on the same token; (4) Alice calls withdrawNftWithInterest(1). The contract deletes Lien[1] and transfers NFT_A to Alice, while Lien[2] is left pointing to a token that has been removed from Jack’s control, resulting in Jack losing the NFT and Bob losing the proceeds from the sale. The impact is a loss of ownership of the NFT and the associated funds for the second lien holder and any market participants, effectively breaking the accounting guarantees of the protocol. The issue was discovered during a security audit that examined the logic of the withdrawal function and identified the missing uniqueness constraint. It is subtle because the function appears to perform the correct checks for lender authorization and loan inactivity, so the erroneous behavior only manifests when multiple liens share the same NFT – a situation that may not be obvious during normal testing. To remediate, the protocol should enforce that each NFT can be bound to at most one active lien, either by rejecting new lien creation when the token is already linked or by adding a verification step in withdrawNftWithInterest that ensures the NFT being transferred is not associated with any other active lien. Additionally, the lien deletion should occur after the transfer and only after confirming that the token ownership matches the lien being withdrawn, thereby preserving the integrity of the accounting model and preventing unauthorized NFT theft.

## Proof of Concept
`withdrawNftWithInterest()` is used to retrieve NFT. The only current restriction is if you can transfer out of NFT, it means an inactive loan.
    
```solidity
function withdrawNftWithInterest(Lien calldata lien, uint256 lienId) external override validateLien(lien, lienId) {
    if (msg.sender != lien.lender) {
        revert Errors.Unauthorized();
    }

    // delete lien
    delete liens[lienId];

    // transfer NFT back to lender
    /// @dev can withdraw means NFT is currently in contract without active loan,
    /// @dev the interest (if any) is already accured to lender at NFT acquiring time
    IERC721(lien.collection).safeTransferFrom(address(this), msg.sender, lien.tokenId);
```

However, the current protocol does not restrict the existence of only one Lien in the same NFT.

For example, the following scenario.

  1. Alice transfers NFT_A and supply Lien[1].
  2. Bob executes `sellNftToMarket()`.
  3. Jack buys NFT_A from the market.
  4. Jack transfers NFT_A and supply Lien[2].
  5. Alice executing `withdrawNftWithInterest(1)` is able to get NFT_A successfully (because step 4 NFT_A is already in the contract). This results in the deletion of lien[1], and Lien[2]‘s NFT_A is transferred away.

The result is: Jack’s NFT is lost and Bob’s funds are also lost.

## Recommendation
Need to determine whether there is a Loan
    
```solidity
function withdrawNftWithInterest(Lien calldata lien, uint256 lienId) external override validateLien(lien, lienId) {
    if (msg.sender != lien.lender) {
        revert Errors.Unauthorized();
    }

    require(lien.loanStartTime == 0,"Active Loan");
```
