# [M] Code uses 0.8.13 which has a Optimiser Bug Regarding Memory Side Effects of Inline Assembly

## Summary
Severity: Medium
Reporter: Jaraxxus
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L7C40-L7C50
Type: audit-issue

## Details
# Code uses 0.8.13 which has a Optimiser Bug Regarding Memory Side Effects of Inline Assembly

## Summary

Solidity version 0.8.13 and 0.8.14 are vulnerable to a recently reported [optimizer bug](https://blog.soliditylang.org/2022/06/15/inline-assembly-memory-side-effects-bug/) related to inline assembly. Solidity 0.8.15 has been released with a fix.

## Vulnerability Detail

Beam's MeritNFT.sol inherits Strings.sol from OpenZeppelin which uses inline assembly, and optimization is enabled while compiling.


```solidity
import "@openzeppelin/contracts/utils/Strings.sol";
```

## Impact

This bug only occurs under very specific conditions: the legacy optimizer must be enabled rather than the IR pipeline (true for the current project configuration), and the affected assembly blocks must not refer to any local Solidity variables.

```solidity
    function toString(uint256 value) internal pure returns (string memory) {
        unchecked {
            uint256 length = Math.log10(value) + 1;
            string memory buffer = new string(length);
            uint256 ptr;
            /// @solidity memory-safe-assembly
            assembly {
                ptr := add(buffer, add(32, length))
            }
            while (true) {
                ptr--;
                /// @solidity memory-safe-assembly
                assembly {
                    mstore8(ptr, byte(mod(value, 10), _SYMBOLS))
                }
                value /= 10;
                if (value == 0) break;
            }
```

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L7C40-L7C50

## Tool used

Manual Review

## Recommendation

Use recent Solidity version 0.8.15 which has the fix for these issues.
