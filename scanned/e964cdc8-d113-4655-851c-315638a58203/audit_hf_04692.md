# [H] AccountV1#flashActionByCreditor can be used

## Summary
Severity: High
Contest weight: 0.7872
Dataset id: 22456
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
AccountV1#flashActionByCreditor is designed to allow atomic flash actions moving funds from the owner of the account. By making the account own itself, these arbitrary calls can be used to transfer ERC721 assets directly out of the account.
The assets being transferred from the account will still show as deposited on the account allowing it to take out loans from creditors without having any actual assets.
The overview of the exploit are as follows:
1) Deposit ERC721
2) Set creditor to malicious designed creditor
3) Transfer the account to itself
4) flashActionByCreditor to transfer ERC721
4a) account owns itself so _transferFromOwner allows transfers from account
4b) Account is now empty but still thinks is has ERC721
5) Use malicious designed liquidator contract to call auctionBoughtIn and transfer account back to attacker
7) Update creditor to legitimate creditor
8) Take out loan against nothing
9) Profit
The key to this exploit is that the account is able to be its own owner. Paired with a maliciously designed creditor (creditor can be set to anything) flashActionByCreditor can be called by the attacker when this is the case.
```solidity
if (transferFromOwnerData.assets.length > 0) {
    _transferFromOwner(transferFromOwnerData, actionTarget);
}
```
In these lines the ERC721 token is transferred out of the account. The issue is that even though the token is transferred out, the erc721Stored array is not updated to reflect this change.
```solidity
function auctionBoughtIn(address recipient) external onlyLiquidator nonReentrant {
    _transferOwnership(recipient);
}
```
As seen above auctionBoughtIn does not have any requirement besides being called by the liquidator. Since the liquidator is also malicious, it can then abuse this function to set the owner to any address, which allows the attacker to recover ownership of the account. Now the attacker has an account that still considers the ERC721 token as owned but that token isn't actually present in the account.
Now the account creditor can be set to a legitimate pool and a loan taken out against no collateral at all.
Account can take out completely uncollateralized loans, causing massive losses to all lending pools.

## Recommendation
The root cause of this issue is that the account can own itself. The fix is simple, make the account unable to own itself by causing transferOwnership to revert if owner == address(this).
