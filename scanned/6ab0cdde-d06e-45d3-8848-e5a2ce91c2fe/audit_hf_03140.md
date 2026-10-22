# [H] Surplus auction cannot be cancelled

## Summary
Severity: High
Contest weight: 0.8587
Dataset id: 17637
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Attempts to cancel surplus auctions will likely fail because approval is required, but not given.  
Instead of performing a conventional transfer(), the token's transferFrom() function is called:  
```solidity
token.transferFrom(address(this), auctions[auctionId].recipient, auctions[auctionId].bid);
```  
However, approval needs to be given to the caller, even if the caller is the token sender. This is the case for OpenZeppelin's ERC20 implementation (which FDT inherits). A snippet of the transferFrom() function is given below.  
```solidity
_transfer(sender, recipient, amount);
uint256 currentAllowance = _allowances[sender][_msgSender()];
require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
```  
Because zero allowance has been given, the transaction will revert.  
Surplus auctions cannot be cancelled.

## Recommendation
Change to transfer() or OpenZeppelin's safeTransfer() methods.  
```solidity
token.transfer(auctions[auctionId].recipient, auctions[auctionId].bid);
```
