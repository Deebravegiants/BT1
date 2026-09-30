# [H] getOraclePrice is prone to manipulation

## Summary
Severity: High
Contest weight: 0.5409
Dataset id: 5547
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getOraclePrice is used to retrieve the latest price from a Velodrome pool. There's a faulty assumption, that if the latest observation's timestamp is in the past, the slot0 price can't have been manipulated, thus it is returned with no extra checks made. The problem is that Velodrome pools write observations once every 15 seconds, therefore allowing for a manipulated price with an outdated observation.
```solidity
if (block.timestamp != blockTimestamp)
    return (spotSqrtPriceX96, spotTick);
```

## Recommendation
Use the latest observation price only if more than 15 seconds have passed since.
