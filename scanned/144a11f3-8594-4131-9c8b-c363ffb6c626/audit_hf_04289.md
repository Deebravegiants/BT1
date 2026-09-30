# [H] H-05 | GMOracleProvider Reverts Due To Incorrect Validation

## Summary
Severity: High
Contest weight: 0.2677
Dataset id: 21428
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMOracleProvider get signed prices from Oracle keepers and tries to validate them with validateSigner(). What is expected from Order Keepers is providing both minPrices and maxPrices in ascending order for a token. The problem occur because these minPrices and maxPrices are validated against their corresponding index in the signers and signatures array. But it is not guaranteed and in most cases won't be possible to both sort minPrices and maxPrices while protecting their corresponding signatures in the correct index. Consider the following scenario: • Oracle Keeper 1 signs minPrice = 1003, maxPrice = 1010 • Oracle Keeper 2 signs minPrice = 1004, maxPrice = 1011 • Oracle Keeper 3 signs minPrice = 1005, maxPrice = 1009 Here when Order Keeper sort both prices in ascending order they will be sorted as follows: minPrice = [Keeper1 minPrice, Keeper2 minPrice, Keeper3 minPrice] maxPrice = [Keeper3 maxPrice, Keeper1 maxPrice, Keeper2 maxPrice] Hence in validateSigner call, prices and respective signatures won't match and call will revert. If on the other hand Order Keeper does not sort the order as above, then sorting check will fail and transaction will again revert.

## Recommendation
Use old indexing system that matches min/maxPrice to their corresponding signers before validating signer.
