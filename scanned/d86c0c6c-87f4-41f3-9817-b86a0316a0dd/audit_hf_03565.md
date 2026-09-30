# [H] Adversary can block `claimAuction`

## Summary
Severity: High
Contest weight: 0.5326
Dataset id: 19408
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`claimAuction()` implements a push-strategy instead of a pull-strategy for returning the bidders funds.

This gives the opportunity for an adversary to DOS the function, locking all funds from other participants.

This finding differs from the automated findings report [M-01](https://github.com/code-423n4/2023-10-nextgen/blob/main/bot-report.md#m-01-unchecked-return-value-of-low-level-calldelegatecall), and [L-18](https://github.com/code-423n4/2023-10-nextgen/blob/main/bot-report.md#l-18-gas-griefingtheft-is-possible-on-an-unsafe-external-call), as it has a different root cause, can’t be prevented with any of the mitigations from the bot, and also highlights the actual High impact of the issue.

## Proof of Concept
An adversary can create bids for as little as 1 wei, as there is no minimum limitation: [AuctionDemo.sol#L58](https://github.com/code-423n4/2023-10-nextgen/blob/main/smart-contracts/AuctionDemo.sol#L58). With that, it can participate in as many auctions as they want to grief all auctions.

All non-winning bidders that didn’t cancel their bid before the auction ended will receive their bids back during `claimAuction()`:
    
    function claimAuction(uint256 _tokenid) public WinnerOrAdminRequired(_tokenid,this.claimAuction.selector){
        /// ...
        for (uint256 i=0; i< auctionInfoData[_tokenid].length; i ++) {
            if (auctionInfoData[_tokenid][i].bidder == highestBidder && auctionInfoData[_tokenid][i].bid == highestBid && auctionInfoData[_tokenid][i].status == true) {
                IERC721(gencore).safeTransferFrom(ownerOfToken, highestBidder, _tokenid);
                (bool success, ) = payable(owner()).call{value: highestBid}("");
                emit ClaimAuction(owner(), _tokenid, success, highestBid);
            } else if (auctionInfoData[_tokenid][i].status == true) {
                (bool success, ) = payable(auctionInfoData[_tokenid][i].bidder).call{value: auctionInfoData[_tokenid][i].bid}("");
                emit Refund(auctionInfoData[_tokenid][i].bidder, _tokenid, success, highestBid);
            } else {}
        }
    }

[AuctionDemo.sol#L116](https://github.com/code-423n4/2023-10-nextgen/blob/main/smart-contracts/AuctionDemo.sol#L116)

The contracts call the bidders with some `value`. If the receiver is a contract, it can execute arbitrary code. A malicious bidder can exploit this to make the `claimAuction()` always revert, and so no funds to other participants be paid back.

With the current implementation, a gas bomb can be implemented to perform the attack. [L-18](https://github.com/code-423n4/2023-10-nextgen/blob/main/bot-report.md#l-18-gas-griefingtheft-is-possible-on-an-unsafe-external-call) from the automated findings report suggests the use of `excessivelySafeCall()` to prevent it, but it limits the functionality of legit contract receivers, and eventually preventing them from receiving the funds. In addition, the finding doesn’t showcase the High severity of the issue and may be neglected.

[M-01](https://github.com/code-423n4/2023-10-nextgen/blob/main/bot-report.md#m-01-unchecked-return-value-of-low-level-calldelegatecall) from the automated findings report points out the lack of a check of the `success` of the calls. If the function reverts when the call was not successful, the adversary can make a callback on its contract `receive()` function to always revert to perform this same attack. In addition, this finding also doesn’t showcase the High severity of the issue.

Ultimately the way to prevent this attack is to separate the transfer of each individual bidder to a separate function.

## Recommendation
Create a separate function for each bidder to claim their funds back (such as the cancel bids functions are implemented).
