# [H] Multiplication could overflow in RebasingLibrary for tokens with greater than 18 decimals

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23409
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: RebasingLibrary contains special handling for tokens with greater than 18 decimals:
// convertTokensToShares
} else {
uint256 scale = 10**(_tokenDecimals - 18);
return (_tokens * DECIMALS_FACTOR + (_rebasingMultiplier * scale) / 2) /
(_rebasingMultiplier * scale);,
!}
// convertSharesToTokens
} else {
uint256 scale = 10**(_tokenDecimals - 18);
return (_shares * _rebasingMultiplier * scale + DECIMALS_FACTOR / 2) / DECIMALS_FACTOR;
}
Impact: When using tokens with high decimal values, the multiplication here could overflow causing denial of
service.

## Recommendation
Recommended Mitigation: Use OpenZeppelin's Math::mulDiv, fixed code also incorporates suggested fix for L-1:
```solidity
pragma solidity 0.8.22;
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
library RebasingLibrary {
    uint256 private constant DECIMALS_FACTOR = 1e18;
    function convertTokensToShares(
        uint256 _tokens,
        uint256 _rebasingMultiplier,
        uint8 _tokenDecimals
    ) internal pure returns (uint256 shares) {
        require(_rebasingMultiplier > 0, "Invalid rebasing multiplier");
        if (_tokenDecimals == 18) {
            return Math.mulDiv(_tokens, DECIMALS_FACTOR, _rebasingMultiplier);
        } else if (_tokenDecimals < 18) {
            uint256 scale = 10**(18 - _tokenDecimals);
            // tokens * scale * DECIMALS_FACTOR / multiplier
            return Math.mulDiv(_tokens * scale, DECIMALS_FACTOR, _rebasingMultiplier);
        } else {
            uint256 scale = 10**(_tokenDecimals - 18);
            // tokens * DECIMALS_FACTOR / (multiplier * scale)
            return Math.mulDiv(_tokens, DECIMALS_FACTOR, _rebasingMultiplier * scale);
        }
    }
    function convertSharesToTokens(
        uint256 _shares,
        uint256 _rebasingMultiplier,
        uint8 _tokenDecimals
    ) internal pure returns (uint256 tokens) {
        require(_rebasingMultiplier > 0, "Invalid rebasing multiplier");
        if (_tokenDecimals == 18) {
            return Math.mulDiv(_shares, _rebasingMultiplier, DECIMALS_FACTOR);
        } else if (_tokenDecimals < 18) {
            uint256 scale = 10**(18 - _tokenDecimals);
            // (shares * multiplier / DECIMALS_FACTOR) / scale
            return Math.mulDiv(_shares, _rebasingMultiplier, DECIMALS_FACTOR * scale);
        } else {
            uint256 scale = 10**(_tokenDecimals - 18);
            // shares * multiplier * scale / DECIMALS_FACTOR
            return Math.mulDiv(_shares * scale, _rebasingMultiplier, DECIMALS_FACTOR);
        }
    }
}
```
