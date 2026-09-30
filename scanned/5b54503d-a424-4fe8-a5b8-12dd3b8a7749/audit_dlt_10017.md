# [?] Merge remote-tracking branch 'origin/fix/underflow' into certora/update-dev

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-28
Source: https://github.com/morpho-org/morpho-blue/commit/e04c7323a87834ab4065f1d4824cd093583b3b36
Type: security-commit

## Details
Merge remote-tracking branch 'origin/fix/underflow' into certora/update-dev

## Patch
### .github/workflows/formatting.yml
```diff
@@ -16,6 +16,9 @@ jobs:
     steps:
       - uses: actions/checkout@v3
 
+      - name: Install Foundry
+        uses: foundry-rs/foundry-toolchain@v1
+
       - name: Install node
         uses: actions/setup-node@v3
         with:
@@ -25,8 +28,5 @@ jobs:
       - name: Install dependencies
         run: yarn install --frozen-lockfile
 
-      - name: Install Foundry
-        uses: foundry-rs/foundry-toolchain@v1
-
       - name: Run Linter
         run: yarn lint
```

### .github/workflows/foundry.yml
```diff
@@ -21,13 +21,13 @@ jobs:
           - type: "slow"
             fuzz-runs: 10000
             max-test-rejects: 500000
-            invariant-runs: 100
-            invariant-depth: 100
+            invariant-runs: 64
+            invariant-depth: 2048
           - type: "fast"
             fuzz-runs: 256
             max-test-rejects: 65536
-            invariant-runs: 256
-            invariant-depth: 15
+            invariant-runs: 16
+            invariant-depth: 256
 
     runs-on: ubuntu-latest
     steps:
```

### .github/workflows/hardhat.yml
```diff
@@ -19,6 +19,9 @@ jobs:
         with:
           submodules: recursive
 
+      - name: Install Foundry
+        uses: foundry-rs/foundry-toolchain@v1
+
       - name: Install node
         uses: actions/setup-node@v3
         with:
@@ -28,9 +31,6 @@ jobs:
       - name: Install dependencies
         run: yarn install --frozen-lockfile
 
-      - name: Install Foundry
-        uses: foundry-rs/foundry-toolchain@v1
-
       - name: Save hardhat cache
         uses: actions/cache@v3
         with:
@@ -40,4 +40,4 @@ jobs:
           key: ${{ github.ref_name }}-hardhat
 
       - name: Run Hardhat tests
-        run: yarn test
+        run: yarn test:hardhat
```

### foundry.toml
```diff
@@ -1,8 +1,27 @@
 [profile.default]
+names = true
+sizes = true
 via-ir = true
 optimizer_runs = 4294967295
 
-[fmt]
+[profile.default.invariant]
+runs = 16
+depth = 256
+fail_on_revert = true
+
+[profile.default.fmt]
 wrap_comments = true
 
+
+[profile.build]
+test = "/dev/null"
+script = "/dev/null"
+force = true
+
+
+[profile.test]
+via-ir = false
+extra_output_files = []
+
+
 # See more config options https://github.com/foundry-rs/foundry/tree/master/crates/config
```

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
@@ -1,28 +1,34 @@
 {
   "scripts": {
-    "postinstall": "husky install",
-    "compile": "npx hardhat compile --force",
-    "test": "npx hardhat test",
-    "lint": "prettier --check test/hardhat && forge fmt --check",
-    "lint:fix": "prettier --write test/hardhat && forge fmt"
+    "postinstall": "husky install && forge install",
+    "build:forge": "FOUNDRY_PROFILE=build forge build",
+    "build:hardhat": "npx hardhat compile --force",
+    "test:forge": "FOUNDRY_PROFILE=test forge test",
+    "test:forge:invariant": "FOUNDRY_MATCH_CONTRACT=InvariantTest yarn test:forge",
+    "test:forge:integration": "FOUNDRY_MATCH_CONTRACT=IntegrationTest yarn test:forge",
+    "test:hardhat": "npx hardhat test",
+    "lint": "yarn lint:forge && yarn lint:hardhat",
+    "lint:forge": "forge fmt --check",
+    "lint:hardhat": "prettier --check test/hardhat",
+    "lint:fix": "yarn lint:forge:fix && yarn lint:hardhat:fix",
+    "lint:forge:fix": "forge fmt",
+    "lint:hardhat:fix": "prettier --write test/hardhat",
+    "clean": "npx hardhat clean && forge clean"
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
@@ -346,8 +347,8 @@ contract Morpho is IMorpho {
         uint256 collateralPrice = IOracle(marketParams.oracle).price();
 
         require(!_isHealthy(marketParams, id, borrower, collateralPrice), ErrorsLib.HEALTHY_POSITION);
-        uint256 repaidAssets;
 
+        uint256 repaidAssets;
         {
             // The liquidation incentive factor is min(maxIncentiveFactor, 1/(1 - cursor*(1 - lltv))).
             uint256 incentiveFactor = UtilsLib.min(
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

### test/forge/InvariantTest.sol
```diff
@@ -3,7 +3,7 @@ pragma solidity ^0.8.0;
 
 import "test/forge/BaseTest.sol";
 
-contract InvariantBaseTest is BaseTest {
+contract InvariantTest is BaseTest {
     using MathLib for uint256;
     using MorphoLib for Morpho;
     using SharesMathLib for uint256;
@@ -19,6 +19,9 @@ contract InvariantBaseTest is BaseTest {
         super.setUp();
 
         targetContract(address(this));
+
+        blockNumber = block.number;
+        timestamp = block.timestamp;
     }
 
     function _targetDefaultSenders() internal {
@@ -153,7 +156,7 @@ contract InvariantBaseTest is BaseTest {
         returns (address randomSenderToLiquidate)
     {
         for (uint256 i; i < addresses.length; ++i) {
-            if (morpho.borrowShares(id, addresses[i]) != 0 && !isHealthy(id, addresses[i])) {
+            if (!isHealthy(id, addresses[i])) {
                 addressArray.push(addresses[i]);
             }
         }
```

### test/forge/integration/AccrueInterestIntegrationTest.sol
```diff
@@ -3,7 +3,7 @@ pragma solidity ^0.8.0;
 
 import "../BaseTest.sol";
 
-contract IntegrationAccrueInterestTest is BaseTest {
+contract AccrueInterestIntegrationTest is BaseTest {
     using MathLib for uint256;
     using MorphoLib for Morpho;
     using SharesMathLib for uint256;
```

### test/forge/integration/AuthorizationIntegrationTest.sol
```diff
@@ -3,7 +3,7 @@ pragma solidity ^0.8.0;
 
 import "../BaseTest.sol";
 
-contract IntegrationAuthorization is BaseTest {
+contract AuthorizationIntegrationTest is BaseTest {
     function testSetAuthorization(address addressFuzz) public {
         vm.assume(addressFuzz != address(this));
 
```
