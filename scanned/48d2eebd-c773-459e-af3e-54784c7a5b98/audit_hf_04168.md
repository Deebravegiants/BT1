# [H] H-02 | twapUpdate Overﬂow DoS

## Summary
Severity: High
Contest weight: 0.1249
Dataset id: 20849
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In MagicLP.sol, _twapUpdate is called every time setReserve or sync is called. The update adds to _BASE_PRICE_CUMULATIVE_LAST_ which is an ever increasing value. In DODO v2, because they use an older version of solidity, it is desired and expected for this value to overﬂow once it has hit the max of type.uint256. However for MagicLP which uses a newer solidity version, this cannot overﬂow and all contract functionality will be bricked.

## Recommendation
Wrap with an unchecked block to allow for overﬂow.
