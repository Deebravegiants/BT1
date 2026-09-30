# [M] `Auction.sol#settleAuction`

## Summary
Severity: Medium
Contest weight: 0.5977
Dataset id: 1287
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Auction.sol#L97-L102](https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Auction.sol#L97-L102)
```solidity
uint256 a = factory.auctionMultiplier() * basket.ibRatio();
uint256 b = (bondBlock - auctionStart) * BASE / factory.auctionDecrement();
uint256 newRatio = a - b;

(address[] memory pendingTokens, uint256[] memory pendingWeights, uint256 minIbRatio) = basket.getPendingWeights();
require(newRatio >= minIbRatio);
```
In the current implementation, `newRatio` is calculated and compared with `minIbRatio` in `settleAuction()`.

However, if `newRatio` is less than `minIbRatio`, `settleAuction()` will always fail and there is no way for the bonder to cancel and get a refund.

## Proof of Concept
Given:

  * `bondPercentDiv` = 400
  * `basketToken.totalSupply` = 40,000
  * `factory.auctionMultiplier` = 2
  * `factory.auctionDecrement` = 10,000
  * `basket.ibRatio` = 1e18
  * `pendingWeights.minIbRatio` = 1.9 * 1e18
  * Alice called `bondForRebalance()` `2,000` blocks after the auction started, paid `100` basketToken for the bond;
  * Alice tries to `settleAuction()`, it will always fail because `newRatio < minIbRatio`;
  * a = 2 * 1e18
  * b = 0.2 * 1e18
  * newRatio = 1.8 * 1e18;
  * Bob calls `bondBurn()` one day after, `100` basketToken from Alice will been burned.

## Recommendation
Move the `minIbRatio` check to `bondForRebalance()`:
```solidity
function bondForRebalance() public override {
    require(auctionOngoing);
    require(!hasBonded);

    bondTimestamp = block.timestamp;
    bondBlock = block.number;

    uint256 a = factory.auctionMultiplier() * basket.ibRatio();
    uint256 b = (bondBlock - auctionStart) * BASE / factory.auctionDecrement();
    uint256 newRatio = a - b;

    (address[] memory pendingTokens, uint256[] memory pendingWeights, uint256 minIbRatio) = basket.getPendingWeights();
    require(newRatio >= minIbRatio);

    IERC20 basketToken = IERC20(address(basket));
    bondAmount = basketToken.totalSupply() / factory.bondPercentDiv();
    basketToken.safeTransferFrom(msg.sender, address(this), bondAmount);
    hasBonded = true;
    auctionBonder = msg.sender;

    emit Bonded(msg.sender, bondAmount);
}
```
While this issue is correct and I think this is a safer way to handle the `require(newRatio >= minIbRatio)` check, there are a few assumptions that are made. For example, it is assumed that the user bonds their tokens without checking `minIbRatio` and a publisher is able to maliciously update `minIbRatio` which must first go through timelock. Based on this, I’m more inclined to downgrade this to `medium` severity as I think this more accurately reflects the threat model.
