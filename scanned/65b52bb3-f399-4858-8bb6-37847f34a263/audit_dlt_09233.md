# [?] Use Math.mulDiv in ERC2981.royaltyInfo to avoid overflow on large salePrice (#6635)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2026-07-26
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/09a3da506314d4ae9acbf78bb19c12e19337e3d0
Type: security-commit

## Details
Use Math.mulDiv in ERC2981.royaltyInfo to avoid overflow on large salePrice (#6635)

## Patch
### contracts/token/common/ERC2981.sol
```diff
@@ -5,6 +5,7 @@ pragma solidity ^0.8.20;
 
 import {IERC2981} from "../../interfaces/IERC2981.sol";
 import {IERC165, ERC165} from "../../utils/introspection/ERC165.sol";
+import {Math} from "../../utils/math/Math.sol";
 
 /**
  * @dev Implementation of the NFT Royalty Standard, a standardized way to retrieve royalty payment information.
@@ -67,7 +68,7 @@ abstract contract ERC2981 is IERC2981, ERC165 {
             royaltyFraction = _defaultRoyaltyInfo.royaltyFraction;
         }
 
-        uint256 royaltyAmount = (salePrice * royaltyFraction) / _feeDenominator();
+        uint256 royaltyAmount = Math.mulDiv(salePrice, royaltyFraction, _feeDenominator());
 
         return (royaltyReceiver, royaltyAmount);
     }
```
