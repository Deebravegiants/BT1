# [H] `_aggregateValidFulfillmentOfferItems

## Summary
Severity: High
Contest weight: 0.4513
Dataset id: 6903
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[FulfillmentApplier.sol#L406](https://github.com/code-423n4/2022-05-opensea-seaport/blob/main/contracts/lib/FulfillmentApplier.sol#L406)  

The `_aggregateValidFulfillmentOfferItems()` function aims to revert on orders with zero value or where a total consideration amount overflows. Internally this is accomplished by having a temporary variable `errorBuffer`, accumulating issues found, and only reverting once all the items are processed in case there was a problem found. This code is optimistic for valid inputs.

Note: there is a similar issue in `_aggregateValidFulfillmentConsiderationItems()`, which is reported separately.

The problem lies in how this `errorBuffer` is updated:
    
    errorBuffer := or(
      errorBuffer,
      or(
        shl(1, lt(newAmount, amount)),
        iszero(mload(amountPtr))
      )
    )

The final error handling code:
    
    switch errorBuffer
    case 1 {
        mstore(0, MissingItemAmount_error_signature)
        revert(0, MissingItemAmount_error_len)
    }
    case 2 {
        throwOverflow()
    }

While the expected value is `0` (success), `1` or `2` (failure), it is possible to set it to `3`, which is unhandled and considered as a “success”. This can be easily accomplished by having both an overflowing item and a zero item in the order list.

This validation error could lead to fulfilling an order with a consideration (potentially ~0) lower than expected.

## Proof of Concept
Craft an offer containing two errors (e.g. with zero amount and overflow).  
Call `matchOrders()`. Via calls to `_matchAdvancedOrders()`, `_fulfillAdvancedOrders()`, `_applyFulfillment()`, `_aggregateValidFulfillmentOfferItems()` will be called.  
The `errorBuffer` will get a value of 3 (the `or` of 1 and 2).  
As the value of 3 is not detected, no error will be thrown and the order will be executed, including the mal formed values.

## Recommendation
1. Change the check on [FulfillmentApplier.sol#L465](https://github.com/code-423n4/2022-05-opensea-seaport/blob/main/contracts/lib/FulfillmentApplier.sol#L465) to consider `case 3`.
2. Potential option: Introduce an early abort in case `errorBuffer != 0` on [FulfillmentApplier.sol#L338](https://github.com/code-423n4/2022-05-opensea-seaport/blob/main/contracts/lib/FulfillmentApplier.sol#L338)

This validation error could lead to fulfilling an order with a consideration (potentially ~0) lower than expected.

That’s correct, you can use this to fulfill an order essentially for free, that’s why I’d consider this high severity. They could have done a better job demonstrating it with a POC test case but this sentence imo shows that they were aware of the impact.

See [this test case](https://github.com/ProjectOpenSea/seaport/blob/5c6a628cb152d731e956682dd748d30e8bf1f1c9/test/findings/FulfillmentOverflowWithMissingItems.spec.ts#L136) showing how to buy an NFT for 1 DAI instead of 1000 DAI.

0age (OpenSea) disagreed with Medium severity:

This is the highest-severity finding. If it were me, I’d switch this to high.

After further consideration and discussion with @HardlyDifficult, we agree with @cmichel that this should be of high severity. As the protocol allows for invalid orders to be created, users aware of this vulnerability will be able to fulfill an order at a considerable discount. This fits the criteria of a high severity issue as it directly leads to lost funds.

[0age (OpenSea) resolved](https://github.com/code-423n4/2022-05-opensea-seaport-findings/issues/75):

PR: [ProjectOpenSea/seaport#320](https://github.com/ProjectOpenSea/seaport/pull/320)
