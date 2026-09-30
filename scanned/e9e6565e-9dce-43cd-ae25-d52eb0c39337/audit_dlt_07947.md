# [?] Resolve npm security vulnerabilities (#1738)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2025-09-24
Source: https://github.com/ava-labs/avalanchego/commit/aecd282620906ce8eef7f736d1573d609f6a9561
Type: security-commit

## Details
Resolve npm security vulnerabilities (#1738)

## Patch
### contracts/contracts/AllowList.sol
```diff
@@ -21,7 +21,7 @@ contract AllowList is Ownable {
     Manager
   }
 
-  constructor(address precompileAddr) Ownable() {
+  constructor(address precompileAddr) Ownable(msg.sender) {
     allowList = IAllowList(precompileAddr);
   }
 
```

### contracts/contracts/ExampleRewardManager.sol
```diff
@@ -10,7 +10,7 @@ address constant REWARD_MANAGER_ADDRESS = 0x020000000000000000000000000000000000
 contract ExampleRewardManager is Ownable {
   IRewardManager rewardManager = IRewardManager(REWARD_MANAGER_ADDRESS);
 
-  constructor() Ownable() {}
+  constructor() Ownable(msg.sender) {}
 
   function currentRewardAddress() public view returns (address) {
     return rewardManager.currentRewardAddress();
```

### contracts/package.json
```diff
@@ -1,18 +1,30 @@
 {
   "name": "@avalabs/subnet-evm-contracts",
   "devDependencies": {
-    "@nomicfoundation/hardhat-chai-matchers": "^2.0.6",
-    "@nomicfoundation/hardhat-toolbox": "^5.0.0",
-    "@types/chai": "^4.3.16",
-    "@types/mocha": "^9.1.1",
-    "@types/node": "^20.12.12",
-    "chai": "^4.4.1",
+    "@nomicfoundation/hardhat-chai-matchers": "^2.1.0",
+    "@nomicfoundation/hardhat-ethers": "^3.1.0",
+    "@nomicfoundation/hardhat-ignition": "^0.15.13",
+    "@nomicfoundation/hardhat-ignition-ethers": "^0.15.14",
+    "@nomicfoundation/hardhat-network-helpers": "^1.1.0",
+    "@nomicfoundation/hardhat-toolbox": "^6.1.0",
+    "@nomicfoundation/hardhat-verify": "^2.1.1",
+    "@nomicfoundation/ignition-core": "^0.15.13",
+    "@typechain/ethers-v6": "^0.5.1",
+    "@typechain/hardhat": "^9.1.0",
+    "@types/chai": "^4.3.20",
+    "@types/mocha": "^10.0.10",
+    "@types/node": "^24.5.2",
+    "chai": "^4.5.0",
     "ds-test": "https://github.com/dapphub/ds-test.git",
-    "hardhat": "^2.22.4",
-    "prettier": "^3.2.4",
-    "prettier-plugin-solidity": "^1.3.1",
+    "ethers": "^6.15.0",
+    "hardhat": "^2.26.3",
+    "hardhat-gas-reporter": "^2.3.0",
+    "prettier": "^3.6.2",
+    "prettier-plugin-solidity": "^2.1.0",
+    "solidity-coverage": "^0.8.16",
     "ts-node": "^10.9.2",
-    "typescript": "^5.4.5"
+    "typechain": "^8.3.2",
+    "typescript": "^5.9.2"
   },
   "version": "1.2.2",
   "description": "",
@@ -35,11 +47,18 @@
     "release:prepare": "rm -rf ./node_modules && npm install && npm run build"
   },
   "dependencies": {
-    "@avalabs/avalanchejs": "^4.0.5",
-    "@openzeppelin/contracts": "^4.9.6"
+    "@avalabs/avalanchejs": "^5.0.0",
+    "@ethersproject/signing-key": "^5.8.0",
+    "@openzeppelin/contracts": "^5.4.0",
+    "@sentry/node": "^10.12.0",
+    "solc": "^0.8.30"
   },
   "engines": {
     "npm": ">7.0.0",
     "node": ">=20.13.0"
+  },
+  "overrides": {
+    "cookie": "^0.7.0",
+    "tmp": "^0.2.3"
   }
-}
\ No newline at end of file
+}
```

### contracts/tasks.ts
```diff
@@ -267,4 +267,4 @@ task("rewardManager:disableRewards", "Disables all rewards, and starts burning f
     const rewardManager = await hre.ethers.getContractAt("IRewardManager", REWARD_MANAGER_ADDDRESS)
     const result = await rewardManager.disableRewards()
     console.log(result)
-  })
+  })
\ No newline at end of file
```
