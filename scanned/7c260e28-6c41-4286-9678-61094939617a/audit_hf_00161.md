# [H] `Basket.sol#auctionBurn`

## Summary
Severity: High
Contest weight: 0.5861
Dataset id: 891
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Given the `auctionBurn()` function will `_burn()` the auction bond without updating the `ibRatio`. Once the bond of a failed auction is burned, the proportional underlying tokens won’t be able to be withdrawn, in other words, being frozen in the contract.

## Proof of Concept
With the configuration of:

basket.ibRatio = 1e18 factory.bondPercentDiv = 400 basket.totalSupply = 400 basket.tokens = [BTC, ETH] basket.weights = [1, 1]

  1. Create an auction;
  2. Bond with 1 BASKET TOKEN;
  3. Wait for 24 hrs and call `auctionBurn()`;

`basket.ibRatio` remains to be 1e18; basket.totalSupply = 399.

Burn 1 BASKET TOKEN will only get back 1 BTC and 1 ETH, which means, there are 1 BTC and 1 ETH frozen in the contract.

## Recommendation
Change to:
```solidity
function auctionBurn(uint256 amount) onlyAuction external override {
    handleFees();
    uint256 startSupply = totalSupply();
    _burn(msg.sender, amount);

    uint256 newIbRatio = ibRatio * startSupply / (startSupply - amount);
    ibRatio = newIbRatio;

    emit NewIBRatio(newIbRatio);
    emit Burned(msg.sender, amount);
}
```
The warden has identified a way for funds to be stuck without a way to recoup them, this is because `ibRatio` is not updated, while `totalSupply` is.

Because this is a specific accounting error, which is effectively a bug in the logic of the protocol, and funds can be irrevocably lost, this is a high severity finding
