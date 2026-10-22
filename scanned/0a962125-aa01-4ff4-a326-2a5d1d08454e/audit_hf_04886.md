# [M] CCTPManager does not support bridging to Ethereum

## Summary
Severity: Medium
Contest weight: 0.3751
Dataset id: 22802
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CCTPManager does not support bridging to Ethereum mainnet.
```solidity
} else if (operation == BridgeLib.OperationType.BRIDGE) {
    uint32 destination = uint32(opParams.extraUInts[1]);
    require(destination != 0, "CCTPManager: invalid destination");
}
```
CCTPManager reverts if the supplied destination for bridging is 0, but 0 is a valid destination referring to the Ethereum mainnet as seen in the CCTP docs. Attempts to bridge USDC to Ethereum mainnet will always revert.

## Recommendation
Remove the requirement that destination != 0.
