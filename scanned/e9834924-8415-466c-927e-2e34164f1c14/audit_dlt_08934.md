# [?] Add reentrancy protection

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2020-08-20
Source: https://github.com/wormhole-foundation/wormhole/commit/085af1d6b7ff5fd66ec81e2410c985ffdecced5e
Type: security-commit

## Details
Add reentrancy protection

## Patch
### ethereum/contracts/Wormhole.sol
```diff
@@ -1,20 +1,19 @@
 // contracts/Wormhole.sol
 // SPDX-License-Identifier: Apache 2
 
-// TODO(hendrik): reentrancy protection for all methods
 // TODO(hendrik): switch-over feature
-// TODO(hendrik): add call for retrying a lockup that the guardian set have refused to sign
 
 pragma solidity ^0.6.0;
 pragma experimental ABIEncoderV2;
 
 import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
 import "@openzeppelin/contracts/math/SafeMath.sol";
+import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
 import "./BytesLib.sol";
 import "./WrappedAsset.sol";
 
-contract Wormhole {
+contract Wormhole is ReentrancyGuard {
     using SafeERC20 for IERC20;
     using BytesLib for bytes;
     using SafeMath for uint256;
@@ -77,7 +76,7 @@ contract Wormhole {
 
     function submitVAA(
         bytes calldata vaa
-    ) public {
+    ) public nonReentrant {
         uint8 version = vaa.toUint8(0);
         require(version == 1, "VAA version incompatible");
 
@@ -208,7 +207,7 @@ contract Wormhole {
         uint256 amount,
         bytes32 recipient,
         uint8 target_chain
-    ) public {
+    ) public nonReentrant {
         require(amount != 0, "amount must not be 0");
 
         uint8 asset_chain = CHAIN_ID;
@@ -234,7 +233,7 @@ contract Wormhole {
     function lockETH(
         bytes32 recipient,
         uint8 target_chain
-    ) public payable {
+    ) public payable nonReentrant {
         require(msg.value != 0, "amount must not be 0");
 
         // Wrap tx value in WETH
```
