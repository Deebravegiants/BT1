# [M] A single precision value may not work for both

## Summary
Severity: Medium
Contest weight: 0.4152
Dataset id: 19834
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The same precision may not work for the min and max prices
If the min price reaches the maximum value possible for the specified level of
precision, the max price won't be able to use the same precision.
Depending on how the order keepers and oracle archive work, either the fetching
the price from the oracle will fail, or the user will get less than they deserve. This
may happen when a user is at the border of being liquidated, and it would be unfair
to liquidate the user.
The same precision is required to be used for both the min and max prices:
```solidity
// File: gmx-synthetics/contracts/oracle/OracleUtils.sol :
OracleUtils.validateSigner()
    bytes32 digest = ECDSA.toEthSignedMessageHash(
        keccak256(abi.encode(
            SALT,
            info.minOracleBlockNumber,
            info.maxOracleBlockNumber,
            info.oracleTimestamp,
            info.blockHash,
            info.token,
            info.tokenOracleType,
            info.precision,
            info.minPrice,
            info.maxPrice
        ))
    );
    address recoveredSigner = ECDSA.recover(digest, signature);
```
occur on precision boundaries.

## Recommendation
Provide separate precision values for min and max prices
