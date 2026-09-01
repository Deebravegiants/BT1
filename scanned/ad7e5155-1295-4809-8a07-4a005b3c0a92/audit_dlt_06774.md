# [H] Reentrancy from matchOneToManyOrders

## Summary
Severity: High
Chain: Smart contract
Component: 2022-06-infinity
Published: 2022-06-19
Source: https://github.com/code-423n4/2022-06-infinity-findings/issues/184
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-infinity/blob/main/contracts/core/InfinityExchange.sol#L178
https://github.com/code-423n4/2022-06-infinity/blob/main/contracts/core/InfinityExchange.sol#L216
https://github.com/code-423n4/2022-06-infinity/blob/main/contracts/core/InfinityExchange.sol#L230


# Vulnerability details

`matchOneToManyOrders` doesn't conform to Checks-Effects-Interactions pattern, and updates the maker order nonce only after the NFTs and payment have been sent.
Using this, a malicious user can re-enter the contract and re-fulfill the order using `takeOrders`.

## Impact
Orders can be executed twice. User funds would be lost.

## Proof of Concept
`matchOneToManyOrders` will set the order nonce as used only after the tokens are being sent:
```
  function matchOneToManyOrders(OrderTypes.MakerOrder calldata makerOrder, OrderTypes.MakerOrder[] calldata manyMakerOrders) external {
    ...
    if (makerOrder.isSellOrder) {
      for (uint256 i = 0; i < ordersLength; ) {
        ...
        _matchOneMakerSellToManyMakerBuys(...); // @audit will transfer tokens in here
        ...
      }
      //@audit setting nonce to be used only here
      isUserOrderNonceExecutedOrCancelled[makerOrder.signer][makerOrder.constraints[5]] = true;
    } else {
      for (uint256 i = 0; i < ordersLength; ) {
        protocolFee += _matchOneMakerBuyToManyMakerSells(...); // @audit will transfer tokens in here
        ...
      }
      //@audit setting nonce to be used only here
      isUserOrderNonceExecutedOrCancelled[makerOrder.signer][makerOrder.constraints[5]] = true;
      ...
  }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-06-infinity-findings/issues/184_
