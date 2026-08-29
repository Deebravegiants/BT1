# [H] A majority attack can easily bypass Zora auction stage in OpenseaProposal and steal the NFT from the party.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-party
Published: 2022-09-19
Source: https://github.com/code-423n4/2022-09-party-findings/issues/264
Type: code-finding

## Details
# Lines of code

https://github.com/PartyDAO/party-contracts-c4/blob/3896577b8f0fa16cba129dc2867aba786b730c1b/contracts/proposals/ListOnZoraProposal.sol#L176-L183


# Vulnerability details

## Description
The PartyGovernance system has many defenses in place to protect against a majority holder stealing the NFT. One of the main protections is that before listing the NFT on Opensea for a proposal-supplied price, it must first try to be auctioned off on Zora. To move from Zora stage to Opensea stage, _settleZoraAuction() is called when executing ListedOnZora step in ListOnOpenseaProposal.sol. If the function returns false, the next step is executed which lists the item on Opensea. It is assumed that if majority attack proposal reaches this stage, it can steal the NFT for free, because it can list the item for negligible price and immediately purchase it from a contract that executes the Opensea proposal. 

Indeed, attacker can always make settleZoraAuction() return false. Looking at  the code:
```
try ZORA.endAuction(auctionId) {
            // Check whether auction cancelled due to a failed transfer during
            // settlement by seeing if we now possess the NFT.
            if (token.safeOwnerOf(tokenId) == address(this)) {
                emit ZoraAuctionFailed(auctionId);
                return false;
            }
        } catch (bytes memory errData) {
```
As the comment already hints, an auction can be cancelled if the NFT transfer to the bidder fails. This is the relevant AuctionHouse code (endAuction):
```
{
            // transfer the token to the winner and pay out the participants below
            try IERC721(auctions[auctionId].tokenContract).safeTransferFrom(address(this), auctions[auctionId].bidder, auctions[auctionId].tokenId) {} catch {
                _handleOutgoingBid(auctions[auctionId].bidder, auctions[auctionId].amount, auctions[auctionId].auctionCurrency);
                _cancelAuction(auctionId);
                return;
 }
```
As most NFTs inherit from OpenZeppelin's ERC721.sol code, safeTransferFrom will run:
```
    function _safeTransfer(
        address from,
        address to,
        uint256 tokenId,
        bytes memory data
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-09-party-findings/issues/264_
