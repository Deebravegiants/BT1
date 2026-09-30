# [M] Proper Handling of isActive in UserProﬁle::_withdraw()

## Summary
Severity: Medium
Contest weight: 0.4211
Dataset id: 12516
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Metatime protocol, the UserProfile contract provides an interface for users to create proﬁles by depositing the supported NFT into the contract. The proﬁles will be deleted after the deposited NFT is withdrawn. To elaborate, we show below the _withdraw() function in the UserProfile contract.
```solidity
function _withdraw() internal returns(bool) {
    User storage u = Users[msg.sender()];
    require(u.isActive, "not active");
    require(u.user_id != address(0), "has not deposited.");
    require(u.user_id == msg.sender(), "not nft owner");
    uint256 tokenID = u.token_id;
    IERC721 nftToken = IERC721(u.NFT_address);
    nftToken.safeTransferFrom(address(this), msg.sender(), tokenID);
    u.user_id = address(0);
    u.NFT_address = address(0);
    u.token_id = 0;
    delete nicknames[u.nickname];
    emit WithdrawNFT(msg.sender(), address(nftToken), tokenID, block.timestamp);
    return true;
}
```
We notice the deletion of a user proﬁle is incomplete. The u.isActive is left as true after the calling of _withdraw(), thus a deleted user would still be able to call updateNickname() to change the nickname. A bad actor may reserve many nicknames by depositing and withdrawing a same NFT multiple times from diﬀerent addresses.

## Recommendation
Improve the user proﬁle deletion logic in UserProfile::_withdraw().
