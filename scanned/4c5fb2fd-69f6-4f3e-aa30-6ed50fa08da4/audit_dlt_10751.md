# [?] Merge branch 'fix/underflow' of github.com:morpho-labs/blue into refactor/test-integration

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-25
Source: https://github.com/morpho-org/morpho-blue/commit/4296cc3872e36ab7295b3155502285218c3eea45
Type: security-commit

## Details
Merge branch 'fix/underflow' of github.com:morpho-labs/blue into refactor/test-integration

## Patch
### hardhat.config.ts
```diff
@@ -1,7 +1,7 @@
 import "@nomicfoundation/hardhat-chai-matchers";
+import "@nomicfoundation/hardhat-ethers";
 import "@nomicfoundation/hardhat-foundry";
 import "@nomicfoundation/hardhat-network-helpers";
-import "@nomiclabs/hardhat-ethers";
 import "@typechain/hardhat";
 import * as dotenv from "dotenv";
 import "ethers-maths";
@@ -47,7 +47,7 @@ const config: HardhatUserConfig = {
     timeout: 3000000,
   },
   typechain: {
-    target: "ethers-v5",
+    target: "ethers-v6",
     outDir: "types/",
     externalArtifacts: ["deps/**/*.json"],
   },
```

### package.json
```diff
@@ -16,22 +16,19 @@
     "clean": "npx hardhat clean && forge clean"
   },
   "dependencies": {
-    "@ethersproject/abi": "^5.7.0",
-    "@ethersproject/bytes": "^5.7.0",
-    "@ethersproject/providers": "^5.7.2",
-    "ethers": "^5.7.2",
-    "ethers-maths": "^3.5.3",
+    "ethers": "^6.7.1",
+    "ethers-maths": "^4.0.2",
     "lodash": "^4.17.21"
   },
   "devDependencies": {
     "@commitlint/cli": "^17.7.1",
     "@commitlint/config-conventional": "^17.7.0",
-    "@nomicfoundation/hardhat-chai-matchers": "^1.0.6",
+    "@nomicfoundation/hardhat-chai-matchers": "^2.0.2",
+    "@nomicfoundation/hardhat-ethers": "^3.0.4",
     "@nomicfoundation/hardhat-foundry": "^1.0.3",
     "@nomicfoundation/hardhat-network-helpers": "^1.0.8",
-    "@nomiclabs/hardhat-ethers": "^2.2.3",
     "@trivago/prettier-plugin-sort-imports": "^4.2.0",
-    "@typechain/ethers-v5": "^11.1.1",
+    "@typechain/ethers-v6": "^0.5.0",
     "@typechain/hardhat": "^9.0.0",
     "@types/chai": "^4.3.5",
     "@types/lodash": "^4.14.197",
```

### src/Morpho.sol
```diff
@@ -272,8 +272,9 @@ contract Morpho is IMorpho {
 
         position[id][onBehalf].borrowShares -= shares.toUint128();
         market[id].totalBorrowShares -= shares.toUint128();
-        market[id].totalBorrowAssets -= assets.toUint128();
+        market[id].totalBorrowAssets = UtilsLib.zeroFloorSub(market[id].totalBorrowAssets, assets).toUint128();
 
+        // `assets` may be greater than `totalBorrowAssets` by 1.
         emit EventsLib.Repay(id, msg.sender, onBehalf, assets, shares);
 
         if (data.length > 0) IMorphoRepayCallback(msg.sender).onMorphoRepay(assets, data);
@@ -366,7 +367,7 @@ contract Morpho is IMorpho {
 
         position[id][borrower].borrowShares -= repaidShares.toUint128();
         market[id].totalBorrowShares -= repaidShares.toUint128();
-        market[id].totalBorrowAssets -= repaidAssets.toUint128();
+        market[id].totalBorrowAssets = UtilsLib.zeroFloorSub(market[id].totalBorrowAssets, repaidAssets).toUint128();
 
         position[id][borrower].collateral -= seizedAssets.toUint128();
 
@@ -383,6 +384,7 @@ contract Morpho is IMorpho {
 
         IERC20(marketParams.collateralToken).safeTransfer(msg.sender, seizedAssets);
 
+        // `repaidAssets` may be greater than `totalBorrowAssets` by 1.
         emit EventsLib.Liquidate(id, msg.sender, borrower, repaidAssets, repaidShares, seizedAssets, badDebtShares);
 
         if (data.length > 0) IMorphoLiquidateCallback(msg.sender).onMorphoLiquidate(repaidAssets, data);
```

### src/libraries/EventsLib.sol
```diff
@@ -78,7 +78,7 @@ library EventsLib {
     /// @param id The market id.
     /// @param caller The caller.
     /// @param onBehalf The address for which the assets were repaid.
-    /// @param assets The amount of assets repaid.
+    /// @param assets The amount of assets repaid. May be 1 over the corresponding market's `totalBorrowAssets`.
     /// @param shares The amount of shares burned.
     event Repay(Id indexed id, address indexed caller, address indexed onBehalf, uint256 assets, uint256 shares);
 
@@ -103,17 +103,17 @@ library EventsLib {
     /// @param id The market id.
     /// @param caller The caller.
     /// @param borrower The borrower of the position.
-    /// @param repaid The amount of assets repaid.
+    /// @param repaidAssets The amount of assets repaid. May be 1 over the corresponding market's `totalBorrowAssets`.
     /// @param repaidShares The amount of shares burned.
-    /// @param seized The amount of collateral seized.
+    /// @param seizedAssets The amount of collateral seized.
     /// @param badDebtShares The amount of shares minted as bad debt.
     event Liquidate(
         Id indexed id,
         address indexed caller,
         address indexed borrower,
-        uint256 repaid,
+        uint256 repaidAssets,
         uint256 repaidShares,
-        uint256 seized,
+        uint256 seizedAssets,
         uint256 badDebtShares
     );
 
```

### src/libraries/UtilsLib.sol
```diff
@@ -28,4 +28,11 @@ library UtilsLib {
         require(x <= type(uint128).max, ErrorsLib.MAX_UINT128_EXCEEDED);
         return uint128(x);
     }
+
+    /// @dev Returns max(x - y, 0).
+    function zeroFloorSub(uint256 x, uint256 y) internal pure returns (uint256 z) {
+        assembly {
+            z := mul(gt(x, y), sub(x, y))
+        }
+    }
 }
```

### test/forge/integration/RepayIntegrationTest.sol
```diff
@@ -127,4 +127,25 @@ contract RepayIntegrationTest is BaseTest {
             "morpho balance"
         );
     }
+
+    function testRepayMax(uint256 shares) public {
+        shares = bound(shares, MIN_TEST_SHARES, MAX_TEST_SHARES);
+
+        uint256 assets = shares.toAssetsUp(0, 0);
+
+        borrowableToken.setBalance(address(this), assets);
+
+        morpho.supply(marketParams, 0, shares, SUPPLIER, hex"");
+
+        collateralToken.setBalance(address(this), HIGH_COLLATERAL_AMOUNT);
+
+        morpho.supplyCollateral(marketParams, HIGH_COLLATERAL_AMOUNT, BORROWER, hex"");
+
+        vm.prank(BORROWER);
+        morpho.borrow(marketParams, 0, shares, BORROWER, RECEIVER);
+
+        borrowableToken.setBalance(address(this), assets);
+
+        morpho.repay(marketParams, 0, shares, BORROWER, hex"");
+    }
 }
```

### test/forge/invariant/SingleMarketChangingPriceInvariantTest.sol
```diff
@@ -175,8 +175,8 @@ contract SingleMarketChangingPriceInvariantTest is InvariantTest {
     }
 
     function invariantMorphoBalance() public {
-        assertEq(
-            morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id), borrowableToken.balanceOf(address(morpho))
+        assertGe(
+            borrowableToken.balanceOf(address(morpho)), morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id)
         );
     }
 }
```

### test/forge/invariant/SingleMarketInvariantTest.sol
```diff
@@ -108,8 +108,8 @@ contract SingleMarketInvariantTest is InvariantTest {
     }
 
     function invariantMorphoBalance() public {
-        assertEq(
-            morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id), borrowableToken.balanceOf(address(morpho))
+        assertGe(
+            borrowableToken.balanceOf(address(morpho)), morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id)
         );
     }
 }
```

### test/forge/invariant/SinglePositionInvariantTest.sol
```diff
@@ -139,7 +139,7 @@ contract SinglePositionInvariantTest is InvariantTest {
     }
 
     function invariantMorphoBalance() public {
-        assertEq(
+        assertGe(
             borrowableToken.balanceOf(address(morpho)), morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id)
         );
     }
```

### test/forge/invariant/TwoMarketsInvariantTest.sol
```diff
@@ -136,6 +136,7 @@ contract TwoMarketsInvariantTest is InvariantTest {
     function invariantMorphoBalance() public {
         uint256 marketAvailableAmount = morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id);
         uint256 market2AvailableAmount = morpho.totalSupplyAssets(id2) - morpho.totalBorrowAssets(id2);
-        assertEq(marketAvailableAmount + market2AvailableAmount, borrowableToken.balanceOf(address(morpho)));
+
+        assertGe(borrowableToken.balanceOf(address(morpho)), marketAvailableAmount + market2AvailableAmount);
     }
 }
```

### test/forge/libraries/UtilsLibTest.sol
```diff
@@ -27,4 +27,8 @@ contract UtilsLibTest is Test {
         vm.expectRevert(bytes(ErrorsLib.MAX_UINT128_EXCEEDED));
         x.toUint128();
     }
+
+    function testZeroFloorSub(uint256 x, uint256 y) public {
+        assertEq(UtilsLib.zeroFloorSub(x, y), x < y ? 0 : x - y);
+    }
 }
```

### test/hardhat/Morpho.spec.ts
```diff
@@ -1,18 +1,15 @@
-import { defaultAbiCoder } from "@ethersproject/abi";
-import { mine } from "@nomicfoundation/hardhat-network-helpers";
-import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers";
+import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";
 import { expect } from "chai";
-import { BigNumber, constants, utils } from "ethers";
-import { parseUnits } from "ethers/lib/utils";
+import { AbiCoder, MaxUint256, keccak256, toBigInt } from "ethers";
 import hre from "hardhat";
 import { Morpho, OracleMock, ERC20Mock, IrmMock } from "types";
 import { MarketParamsStruct } from "types/src/Morpho";
 import { FlashBorrowerMock } from "types/src/mocks/FlashBorrowerMock";
 
 const closePositions = false;
 // Without the division it overflows.
-const initBalance = constants.MaxUint256.div(parseUnits("10000000000000000"));
-const oraclePriceScale = parseUnits("1", 36);
+const initBalance = MaxUint256 / 10000000000000000n;
+const oraclePriceScale = 1000000000000000000000000000000000000n;
 
 let seed = 42;
 const random = () => {
@@ -22,12 +19,12 @@ const random = () => {
 };
 
 const identifier = (marketParams: MarketParamsStruct) => {
-  const encodedMarket = defaultAbiCoder.encode(
+  const encodedMarket = AbiCoder.defaultAbiCoder().encode(
     ["address", "address", "address", "address", "uint256"],
     Object.values(marketParams),
   );
 
-  return Buffer.from(utils.keccak256(encodedMarket).slice(2), "hex");
+  return Buffer.from(keccak256(encodedMarket).slice(2), "hex");
 };
 
 describe("Morpho", () => {
@@ -80,33 +77,35 @@ describe("Morpho", () => {
     irm = await IrmMockFactory.deploy();
 
     updateMarket({
-      borrowableToken: borrowable.address,
-      collateralToken: collateral.address,
-      oracle: oracle.address,
-      irm: irm.address,
-      lltv: BigNumber.WAD.div(2).add(1),
+      borrowableToken: await borrowable.getAddress(),
+      collateralToken: await collateral.getAddress(),
+      oracle: await oracle.getAddress(),
+      irm: await irm.getAddress(),
+      lltv: BigInt.WAD / 2n + 1n,
     });
 
     await morpho.enableLltv(marketParams.lltv);
     await morpho.enableIrm(marketParams.irm);
     await morpho.createMarket(marketParams);
 
+    const morphoAddress = await morpho.getAddress();
+
     for (const signer of signers) {
       await borrowable.setBalance(signer.address, initBalance);
-      await borrowable.connect(signer).approve(morpho.address, constants.MaxUint256);
+      await borrowable.connect(signer).approve(morphoAddress, MaxUint256);
       await collateral.setBalance(signer.address, initBalance);
-      await collateral.connect(signer).approve(morpho.address, constants.MaxUint256);
+      await collateral.connect(signer).approve(morphoAddress, MaxUint256);
     }
 
     await borrowable.setBalance(admin.address, initBalance);
-    await borrowable.connect(admin).approve(morpho.address, constants.MaxUint256);
+    await borrowable.connect(admin).approve(morphoAddress, MaxUint256);
 
     await borrowable.setBalance(liquidator.address, initBalance);
-    await borrowable.connect(liquidator).approve(morpho.address, constants.MaxUint256);
+    await borrowable.connect(liquidator).approve(morphoAddress, MaxUint256);
 
     const FlashBorrowerFactory = await hre.ethers.getContractFactory("FlashBorrowerMock", admin);
 
-    flashBorrower = await FlashBorrowerFactory.deploy(morpho.address);
+    flashBorrower = await FlashBorrowerFactory.deploy(morphoAddress);
   });
 
   it("should simulate gas cost [main]", async () => {
@@ -115,20 +114,20 @@ describe("Morpho", () => {
 
       const user = signers[i];
 
-      let assets = BigNumber.WAD.mul(1 + Math.floor(random() * 100));
+      let assets = BigInt.WAD * toBigInt(1 + Math.floor(random() * 100));
 
-      await morpho.connect(user).supply(marketParams, assets, 0, user.address, []);
-      await morpho.connect(user).withdraw(marketParams, assets.div(2), 0, user.address, user.address);
+      await morpho.connect(user).supply(marketParams, assets, 0, user.address, "0x");
+      await morpho.connect(user).withdraw(marketParams, assets / 2n, 0, user.address, user.address);
       const totalSupplyAssets = (await morpho.market(id)).totalSupplyAssets;
       const totalBorrowAssets = (await morpho.market(id)).totalBorrowAssets;
-      const liquidity = BigNumber.from(totalSupplyAssets).sub(BigNumber.from(totalBorrowAssets));
+      const liquidity = totalSupplyAssets - totalBorrowAssets;
 
-      assets = BigNumber.min(assets, BigNumber.from(liquidity).div(2));
+      assets = BigInt.min(assets, liquidity / 2n);
 
-      await morpho.connect(user).supplyCollateral(marketParams, assets, user.address, []);
-      await morpho.connect(user).borrow(marketParams, assets.div(2), 0, user.address, user.address);
-      await morpho.connect(user).repay(marketParams, assets.div(4), 0, user.address, []);
-      await morpho.connect(user).withdrawCollateral(marketParams, assets.div(8), user.address, user.address);
+      await morpho.connect(user).supplyCollateral(marketParams, assets, user.address, "0x");
+      await morpho.connect(user).borrow(marketParams, assets / 2n, 0, user.address, user.address);
+      await morpho.connect(user).repay(marketParams, assets / 4n, 0, user.address, "0x");
+      await morpho.connect(user).withdrawCollateral(marketParams, assets / 8n, user.address, user.address);
     }
 
     await hre.network.provider.send("evm_setAutomine", [true]);
@@ -141,9 +140,9 @@ describe("Morpho", () => {
       const user = signers[i];
       const borrower = signers[nbLiquidations + i];
 
-      const lltv = BigNumber.WAD.mul(i + 1).div(nbLiquidations + 1);
-      const assets = BigNumber.WAD.mul(1 + Math.floor(random() * 100));
-      const borrowedAmount = assets.wadMulDown(lltv.sub(1));
+      const lltv = (BigInt.WAD * toBigInt(i + 1)) / toBigInt(nbLiquidations + 1);
+      const assets = BigInt.WAD * toBigInt(1 + Math.floor(random() * 100));
+      const borrowedAmount = assets.wadMulDown(lltv - 1n);
 
       if (!(await morpho.isLltvEnabled(lltv))) {
         await morpho.enableLltv(lltv);
@@ -161,29 +160,31 @@ describe("Morpho", () => {
       await morpho.connect(borrower).supplyCollateral(marketParams, assets, borrower.address, "0x");
       await morpho.connect(borrower).borrow(marketParams, borrowedAmount, 0, borrower.address, user.address);
 
-      await oracle.setPrice(oraclePriceScale.div(1000));
+      await oracle.setPrice(oraclePriceScale / 1000n);
 
-      const seized = closePositions ? assets : assets.div(2);
+      const seized = closePositions ? assets : assets / 2n;
 
       await morpho.connect(liquidator).liquidate(marketParams, borrower.address, seized, 0, "0x");
 
       const remainingCollateral = (await morpho.position(id, borrower.address)).collateral;
 
       if (closePositions)
-        expect(remainingCollateral.isZero(), "did not take the whole collateral when closing the position").to.be.true;
-      else expect(!remainingCollateral.isZero(), "unexpectedly closed the position").to.be.true;
+        expect(remainingCollateral === 0n, "did not take the whole collateral when closing the position").to.be.true;
+      else expect(remainingCollateral !== 0n, "unexpectedly closed the position").to.be.true;
 
       await oracle.setPrice(oraclePriceScale);
     }
   });
 
   it("should simuate gas cost [flashLoans]", async () => {
     const user = signers[0];
-    const assets = BigNumber.WAD;
+    const assets = BigInt.WAD;
 
     await morpho.connect(user).supply(marketParams, assets, 0, user.address, "0x");
 
-    const data = defaultAbiCoder.encode(["address"], [borrowable.address]);
-    await flashBorrower.flashLoan(borrowable.address, assets.div(2), data);
+    const borrowableAddress = await borrowable.getAddress();
+
+    const data = AbiCoder.defaultAbiCoder().encode(["address"], [borrowableAddress]);
+    await flashBorrower.flashLoan(borrowableAddress, assets / 2n, data);
   });
 });
```
