# [H] H-04 | Price Query Failure Due To Transient Storage In PricingManager

## Summary
Severity: High
Contest weight: 0.2041
Dataset id: 2094
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PricingManager contract relies on transient storage to store and read price data. As a result,
once the transaction that calls setPrices completes, the stored price data is cleared. Subsequent
operations in a new transaction that rely on _priceOf as for example withdrawAllCollateral fail to
retrieve valid prices, returning zero and reverting due to the require check.
This leads to a DoS scenario where users will not be able to perform certain operations that rely on
the PricingManager returned price. Currently, the only operation that is affected is
withdrawAllCollateral as this is the only function in the OrderBook that does not have to be called by
a broker and uses the _priceOf function, querying the transient storage.

## Recommendation
Switch to a permanent storage mechanism within PricingManager so that prices remain available
across transactions. If the use of transient storage is still wanted, ensure all functions relying on
_priceOf are executed within the same transaction that sets the price.
