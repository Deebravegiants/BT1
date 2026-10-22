# [M] Packed configs in CommandLib wrongly use 1 extra bit for custom flags

## Summary
Severity: Medium
Contest weight: 0.4303
Dataset id: 13545
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In CommandLib, commands are specified using packed configs of 20 bits: uint256 internal constant PACKED_CONFIG_TARGET_CONFIG_BITS = 5; uint256 internal constant PACKED_CONFIG_SIZE_BITS = 20; In each packed config, the first 5 bits are used for custom flags, leaving only 15 bits for the currency index. However, in _executeCommand(), the currency index is read from each packed config as such: int256 currencyIndex = uint16(pc >> PACKED_CONFIG_TARGET_CONFIG_BITS) - 1; pc is shifted right by 5 bits, and then the next 16 bits are read. This causes 1 extra bit to be read from the next packed config. If the first custom flag (LSB) for the next packed config is set, currencyIndex will include this 1 extra bit, causing it to be wrong. For example:
```solidity
function testPackedConfig() public {
    uint256 index = 1;
    uint256 flags = 1; // 00001
    uint256 config = (index << PACKED_CONFIG_TARGET_CONFIG_BITS) | flags; // ...0100001
    uint256 packedConfig = config << PACKED_CONFIG_SIZE_BITS | config;
    uint256 currencyIndex = uint16(packedConfig >> PACKED_CONFIG_TARGET_CONFIG_BITS) -
        1;
    console2.log(currencyIndex); // 32768 instead of 0
}
```
The impact is that redeem() and redeemK() in the Index contract will unexpectedly revert when custom flags are used since the code will perform an out-of-bounds access to the currencyStates array.

## Recommendation
Use 4 bits for custom flags instead, leaving 16 bits for the currency index:
- uint256 internal constant PACKED_CONFIG_TARGET_CONFIG_BITS = 5;
+ uint256 internal constant PACKED_CONFIG_TARGET_CONFIG_BITS = 4;
