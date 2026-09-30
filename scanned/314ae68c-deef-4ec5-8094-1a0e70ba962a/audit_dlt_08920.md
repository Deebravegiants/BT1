# [?] evm/token_bridge: reentrancy protection

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2022-01-20
Source: https://github.com/wormhole-foundation/wormhole/commit/608c724a76249689de4b8e0e48bd4785f249435b
Type: security-commit

## Details
evm/token_bridge: reentrancy protection

## Patch
### ethereum/contracts/bridge/Bridge.sol
```diff
@@ -3,6 +3,7 @@
 
 pragma solidity ^0.8.0;
 
+import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
 import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 
@@ -16,7 +17,7 @@ import "./BridgeGovernance.sol";
 import "./token/Token.sol";
 import "./token/TokenImplementation.sol";
 
-contract Bridge is BridgeGovernance {
+contract Bridge is BridgeGovernance, ReentrancyGuard {
     using BytesLib for bytes;
 
     // Produce a AssetMeta message for a given token
@@ -90,7 +91,7 @@ contract Bridge is BridgeGovernance {
     }
 
     // Initiate a Transfer
-    function transferTokens(address token, uint256 amount, uint16 recipientChain, bytes32 recipient, uint256 arbiterFee, uint32 nonce) public payable returns (uint64 sequence) {
+    function transferTokens(address token, uint256 amount, uint16 recipientChain, bytes32 recipient, uint256 arbiterFee, uint32 nonce) public payable nonReentrant returns (uint64 sequence) {
         // determine token parameters
         uint16 tokenChain;
         bytes32 tokenAddress;
```
