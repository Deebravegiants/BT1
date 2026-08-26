# [H] When _bridgeType is equal to 1, the "Across bridge" transaction may fail and result in user fund lock because of the insufficient input validation in _bridgeAssetDirect

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/106
Type: sherlock-finding

## Details
ctf_sec

high

# When _bridgeType is equal to 1, the "Across bridge" transaction may fail and result in user fund lock because of the insufficient input validation in _bridgeAssetDirect

## Summary

When _bridgeType is equal to 1, the "Across bridge" transaction may fail because of insufficient input validation in _bridgeAssetDirect

## Vulnerability Detail

this is the current implementation may to handle the bridge transaction if the bridge type is set to 1 is

```solidity
 if (_bridgeType == 1) {
    // Across bridge can be called through defined interface, the variable of fee percentage
    // is depending on gas price conditions in the target chain and is retrieved by the
    // application off-chain by calling the Across bridge API
    uint256 feePct;
    assembly {
        // offset 0x20 to data and 0x14 to tightly packed address, at offset 0x34 32 bytes expected are fee pct
        feePct := mload(add(_bridgeTxData, 0x34))
    }
    IAcrossBridgeSpokePool(targetAddress).deposit(
        cardPartnerAddress,
        cardTopupToken,
        _amount,
        1, // L1 Eth mainnet
        uint64(feePct), // max is 495_000_000_000_000_000 (49.5%) fee (bridge has 50% fee allowed as max)
        uint32(block.timestamp));
}
```

Let's layout the parameter for this crucial function deposit

```solidity
// Interface to represent Across bridge spoke pool on L2
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/106_
