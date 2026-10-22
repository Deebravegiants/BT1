# [H] A malicious lien owner can exploit a reentrancy in auctions

## Summary
Severity: High
Contest weight: 0.3122
Dataset id: 17707
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious lien owner can exploit a reentrancy in auctions to have their liens removed without making their payments and thus stealing LP funds. A malicious lien owner can exploit a reentrancy from the callback to decreaseYIntercept() in endAuction() to call cancelAuction() and then take a new loan whose lien token is removed when control returns back to endAuction(). PoC: https://gist.github.com/lucyoa/901a7713fded73293b5e4f9452344c5a Exploit scenario sequence:
1. Strategist creates the public vault
2. Liquidity provider puts 50 ETH into vault
3. Malicious borrower takes a loan of 10 ETH by depositing NFT
4. Borrower buys out their own lien via _buyoutLien by paying 10ETH + fee
5. Borrower does not repay within lien duration to trigger liquidation
6. Borrower (or someone else) triggers endAuction()
7. Execution flow gets hijacked by borrower (lien token owner) inside call to decreaseYIntercept():
   - Borrower cancels auction by paying reservePrice+initiatorFee (this would also go to borrower if setPayee is set before the auction as the owner of that Lien token)
   - Borrower releases NFT to themselves
   - Borrower now takes another loan of 50 ETH with the same NFT, vault and commitment
8. Once control returns to AuctionHouse.endAuction, borrower's new loan's Lien token is deleted
9. CollateralToken.endAuction releases borrower's NFT to borrower
10. Malicious borrower steals 50 ETH from vault without any outstanding liens resulting in LP fund loss

## Recommendation
1. Maintain a mapping of active public vaults.
2. Account for malicious lien token owners via lien buyouts.
3. Use reentrancy guards.
