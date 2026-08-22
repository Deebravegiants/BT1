# [H] In `AuctionManager` contract: cancelling a bid by the original bidder doesn't fully remove the bid which might lead to the same bid being re-activated by the manager

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-08
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/29
Type: hats-finding

## Details
**Github username:** @@DevHals
**Submission hash (on-chain):** 0x36d22b6619524fd2e86dc393935b477f7bb867d94ec9dfa4d45ccd73be5fb428
**Severity:** high

**Description:**
**Description**
- In `AuctionManager` contract: any whitelisted node operator can create a bid/bids; when doing so, they send the contract an amount of native tokens equals to the `_bidSize * _bidAmountPerBid`.

- The bidder (bid creator) can cancel the bid by calling `AuctionManager.cancelBid` function; where the bid is deactivated (`bid.isActive = false`) and the bid amount is sent back to the bidder.

  ```solidity
  function _cancelBid(uint256 _bidId) internal {
        Bid storage bid = bids[_bidId];
        require(bid.bidderAddress == msg.sender, "Invalid bid");
        require(bid.isActive, "Bid already cancelled");

        // Cancel the bid by de-activating it
        bid.isActive = false;
        numberOfActiveBids--;

        // Refund the user with their bid amount
        (bool sent, ) = msg.sender.call{value: bid.amount}("");
        require(sent, "Failed to send Ether");

        emit BidCancelled(_bidId);
     }
  ```

- As can be noticed; the bid is not deleted from the `bids` array; only its activity is set to `false`.
- 
**Attack Scenario**
- The `AuctionManager` contract has a functionality that enables the `StakingManagerContract` from deactivating any active bid (setting ` bid.isActive = false`) by calling the `updateSelectedBidInformation` function, and again it can activate the bid by calling `reEnterAuction` on the deactivated bid.

- But the `reEnterAuction` can be called on a bid that has been cancelled by the bidder (where he was refunded the bid amount).

- So if the `reEnterAuction` function is called on the withdrawn bid; the bidder can re-cancel this bid again and get the value of the bid for the second time, which will result in contract losing from its funds.

**Attachments**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/29_
