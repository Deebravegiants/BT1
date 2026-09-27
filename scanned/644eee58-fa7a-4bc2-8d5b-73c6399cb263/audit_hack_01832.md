# [H] Price and refund changes may cause failures

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Price and refund for gold cards are used in 3 different places: commit, mint, refund.

Weave tokens spent during the commit phase


**code/contracts/shop/GoldCardsFactory.sol:L274-L279**
```solidity
function _commit(uint256 _weaveAmount, GoldOrder memory _order)
  internal
{
  // Check if weave sent is sufficient for order
  uint256 total_cost = _order.cardAmount.mul(goldPrice).add(_order.feeAmount);
  uint256 refund_amount = _weaveAmount.sub(total_cost); // Will throw if insufficient amount received
```

but they are burned `rngDelay` blocks after 


**code/contracts/shop/GoldCardsFactory.sol:L371-L373**
```solidity
// Burn the non-refundable weave
uint256 weave_to_burn = (_order.cardAmount.mul(goldPrice)).sub(_order.cardAmount.mul(goldRefund));
weaveContract.burn(weaveID, weave_to_burn);
```

If the price is increased between these transactions, mining cards may fail because it should burn more `weave` tokens than there are tokens in the smart contract. Even if there are enough tokens during this particular transaction, someone may fail to melt a gold card later. 

If the price is decreased, some `weave` tokens will be stuck in the contract forever without being burned.

#### Recommendation

Store `goldPrice` and `goldRefund` in `GoldOrder`.
