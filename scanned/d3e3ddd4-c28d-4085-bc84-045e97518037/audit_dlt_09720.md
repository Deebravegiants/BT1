# [?] audit fix: L-01 Denial of Service in withdrawEther via Donation

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2026-01-14
Source: https://github.com/etherfi-protocol/smart-contracts/commit/14d9d2a27f759ec414e11aa1912f8474da9a6544
Type: security-commit

## Details
audit fix: L-01 Denial of Service in withdrawEther via Donation

## Patch
### src/EtherFiNode.sol
```diff
@@ -126,7 +126,9 @@ contract EtherFiNode is IEtherFiNode {
         if (!anyWithdrawalsCompleted) revert NoCompleteableWithdrawals(); // bad dev experience if function completes but nothing happened
 
         // if there are available rewards, forward them to the liquidityPool
-        uint256 balance = address(this).balance;
+        uint256 contractBalance = address(this).balance;
+        uint256 totalValueOutOfLp = liquidityPool.totalValueOutOfLp();
+        uint256 balance = contractBalance < totalValueOutOfLp ? contractBalance : totalValueOutOfLp;
         if (balance > 0) {
             (bool sent, ) = payable(address(liquidityPool)).call{value: balance, gas: 20000}("");
             if (!sent) revert TransferFailed();
@@ -155,7 +157,9 @@ contract EtherFiNode is IEtherFiNode {
     // @dev under normal operations it is not expected for eth to accumulate in the nodes,
     //    this is just to handle any exceptional cases such as someone sending directly to the node.
     function sweepFunds() external onlyEtherFiNodesManager returns (uint256 balance) {
-        uint256 balance = address(this).balance;
+        uint256 contractBalance = address(this).balance;
+        uint256 totalValueOutOfLp = liquidityPool.totalValueOutOfLp();
+        balance = contractBalance < totalValueOutOfLp ? contractBalance : totalValueOutOfLp;
         if (balance > 0) {
             (bool sent, ) = payable(address(liquidityPool)).call{value: balance, gas: 20000}("");
             if (!sent) revert TransferFailed();
```

### src/EtherFiRestaker.sol
```diff
@@ -142,7 +142,7 @@ contract EtherFiRestaker is Initializable, UUPSUpgradeable, OwnableUpgradeable,
 
     // Send the ETH back to the liquidity pool
     function withdrawEther() public onlyAdmin {
-        uint256 amountToLiquidityPool = address(this).balance;
+        uint256 amountToLiquidityPool = _min(address(this).balance, liquidityPool.totalValueOutOfLp());
         (bool sent, ) = payable(address(liquidityPool)).call{value: amountToLiquidityPool, gas: 20000}("");
         require(sent, "ETH_SEND_TO_LIQUIDITY_POOL_FAILED");
     }
```

### src/EtherFiRewardsRouter.sol
```diff
@@ -7,6 +7,7 @@ import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 
 import "./RoleRegistry.sol";
+import "./interfaces/ILiquidityPool.sol";
 
 contract EtherFiRewardsRouter is OwnableUpgradeable, UUPSUpgradeable  {
     using SafeERC20 for IERC20;
@@ -43,7 +44,9 @@ contract EtherFiRewardsRouter is OwnableUpgradeable, UUPSUpgradeable  {
 
     function withdrawToLiquidityPool() external {
 
-        uint256 balance = address(this).balance;
+        uint256 contractBalance = address(this).balance;
+        uint256 totalValueOutOfLp = ILiquidityPool(payable(liquidityPool)).totalValueOutOfLp();
+        uint256 balance = contractBalance < totalValueOutOfLp ? contractBalance : totalValueOutOfLp;
         require(balance > 0, "Contract balance is zero");
         (bool success, ) = liquidityPool.call{value: balance}("");
         require(success, "TRANSFER_FAILED");
```

### src/Liquifier.sol
```diff
@@ -184,7 +184,7 @@ contract Liquifier is Initializable, UUPSUpgradeable, OwnableUpgradeable, Pausab
 
     // Send the redeemed ETH back to the liquidity pool & Send the fee to Treasury
     function withdrawEther() external onlyAdmin {
-        uint256 amountToLiquidityPool = address(this).balance;
+        uint256 amountToLiquidityPool = _min(address(this).balance, liquidityPool.totalValueOutOfLp());
         (bool sent, ) = payable(address(liquidityPool)).call{value: amountToLiquidityPool, gas: 20000}("");
         if (!sent) revert EthTransferFailed();
     }
```
