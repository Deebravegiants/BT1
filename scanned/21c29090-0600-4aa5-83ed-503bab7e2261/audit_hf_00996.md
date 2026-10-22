# [H] WithdrawProxy allows redemptions before PublicVault calls transferWithdrawReserve

## Summary
Severity: High
Contest weight: 0.5845
Dataset id: 3222
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anytime there is a withdraw pending (i.e. someone holds WithdrawProxy shares), shares may be redeemed so long as totalAssets() > 0 and s.finalAuctionEnd == 0.  
Under normal operating conditions totalAssets() becomes greater than 0 when the PublicVault calls transferWithdrawReserve.  
totalAssets() can also be increased to a non-zero value by anyone transferring WETH to the contract.  
If this occurs and a user attempts to redeem, they will receive a smaller share than they are owed.  
Exploit scenario:  
• Depositor redeems from PublicVault and receives WithdrawProxy shares.  
• Malicious actor deposits a small amount of WETH into the WithdrawProxy.  
• Depositor accidentally redeems, or is tricked into redeeming, from the WithdrawProxy while totalAssets() is smaller than it should be.  
• PublicVault properly processes epoch and full withdrawReserve is sent to WithdrawProxy.  
• All remaining holders of WithdrawProxy shares receive an outsized share as the previous shares were redeemed for the incorrect value.

## Recommendation
• Option 1:  
Consider being explicit in opening the WithdrawProxy for redemptions (redeem/withdraw) by requiring s.withdrawReserveReceived to be a non-zero value:
```solidity
if (s.finalAuctionEnd != 0 || s.withdrawReserveReceived == 0) {
    // if finalAuctionEnd is 0, no auctions were added
    revert InvalidState(InvalidStates.NOT_CLAIMED);
}
```
