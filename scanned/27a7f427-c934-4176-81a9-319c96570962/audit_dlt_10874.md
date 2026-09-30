# [?] Fix nondeterministic router compile (#478)

## Summary
Severity: Unknown
Chain: Synthetix
Component: Synthetixio/synthetix-v3
Published: 2021-11-25
Source: https://github.com/Synthetixio/synthetix-v3/commit/0ad050cfe76e675e37436a6eb63e67c614e5ae21
Type: security-commit

## Details
Fix nondeterministic router compile (#478)

* More explicit compiler settings

* Remove kovan deployment

* Remove variable data from Solidity comments

* Clean deployment on kovan

## Patch
### packages/core-modules/hardhat.config.js
```diff
@@ -3,7 +3,15 @@ require('@nomiclabs/hardhat-ethers');
 require('@synthetixio/deployer');
 
 module.exports = {
-  solidity: '0.8.4',
+  solidity: {
+    version: '0.8.7',
+    settings: {
+      optimizer: {
+        enabled: true,
+        runs: 200,
+      },
+    },
+  },
   networks: {
     local: {
       url: 'http://localhost:8545',
```

### packages/deployer/subtasks/generate-router.js
```diff
@@ -3,8 +3,6 @@ const path = require('path');
 const filterValues = require('filter-values');
 const { subtask } = require('hardhat/config');
 const logger = require('@synthetixio/core-js/utils/logger');
-const { getCommit, getBranch } = require('@synthetixio/core-js/utils/git');
-const { readPackageJson } = require('@synthetixio/core-js/utils/npm');
 const relativePath = require('@synthetixio/core-js/utils/relative-path');
 const { renderTemplate } = require('../internal/generate-contracts');
 const { getAllSelectors } = require('../internal/contract-helper');
@@ -34,18 +32,7 @@ subtask(
 
   const binaryData = _buildBinaryData({ selectors });
 
-  let packageJson;
-  try {
-    packageJson = readPackageJson();
-  } catch (err) {
-    packageJson = { name: '' };
-  }
-
   const generatedSource = renderTemplate(hre.deployer.paths.routerTemplate, {
-    project: packageJson.name,
-    repo: packageJson.repository?.url || '',
-    branch: getBranch(),
-    commit: getCommit(),
     moduleName: routerName,
     modules: _renderModules(modules),
     selectors: _renderSelectors({ binaryData }),
```

### packages/deployer/templates/Router.sol.mustache
```diff
@@ -3,13 +3,6 @@ pragma solidity ^0.8.0;
 
 // --------------------------------------------------------------------------------
 // --------------------------------------------------------------------------------
-// {{{project}}}
-//
-// Source code generated from
-// Repository: {{{repo}}}
-// Branch: {{{branch}}}
-// Commit: {{{commit}}}
-//
 // GENERATED CODE - do not edit manually!!
 // --------------------------------------------------------------------------------
 // --------------------------------------------------------------------------------
```

### packages/deployer/test/fixture-projects/custom-proxy/hardhat.config.js
```diff
@@ -2,7 +2,15 @@ require('@nomiclabs/hardhat-ethers');
 require('../../..');
 
 module.exports = {
-  solidity: '0.8.4',
+  solidity: {
+    version: '0.8.7',
+    settings: {
+      optimizer: {
+        enabled: true,
+        runs: 200,
+      },
+    },
+  },
   deployer: {
     proxyContract: 'CustomProxy',
   },
```

### packages/deployer/test/fixture-projects/namespace-collision/hardhat.config.js
```diff
@@ -2,7 +2,15 @@ require('@nomiclabs/hardhat-ethers');
 require('../../..');
 
 module.exports = {
-  solidity: '0.8.4',
+  solidity: {
+    version: '0.8.7',
+    settings: {
+      optimizer: {
+        enabled: true,
+        runs: 200,
+      },
+    },
+  },
   networks: {
     local: {
       url: 'http://localhost:8545',
```

### packages/deployer/test/fixture-projects/sample-project/hardhat.config.js
```diff
@@ -2,7 +2,15 @@ require('@nomiclabs/hardhat-ethers');
 require('../../..');
 
 module.exports = {
-  solidity: '0.8.4',
+  solidity: {
+    version: '0.8.7',
+    settings: {
+      optimizer: {
+        enabled: true,
+        runs: 200,
+      },
+    },
+  },
   networks: {
     local: {
       url: 'http://localhost:8545',
```

### packages/synthetix-main/deployments/kovan/official/2021-11-17-00.json
```diff
@@ -1,68 +0,0 @@
-{
-  "properties": {
-    "completed": true,
-    "totalGasUsed": "4822199"
-  },
-  "transactions": {
-    "0xee37a84183f5f514aadb09a2d4d7f1dca435845f138c041a8df8fb215b8be1fd": {
-      "status": "confirmed"
-    },
-    "0xc0ef9eff7520641e678178541af840b458010af7f5049485b643f4afc9c18736": {
-      "status": "confirmed"
-    },
-    "0xba7b7d147e921293d78ec566ac0d2320e25045a93b5cbd8b461a1fe496cd148d": {
-      "status": "confirmed"
-    },
-    "0x00b0eda8b8a9e81dc3775707630756bdb913ecbe2d9e711dadd8016f2c4e830d": {
-      "status": "confirmed"
-    },
-    "0x38c4bc09f33a2dd9318b5349ad770fee0fb678134dfaf03e60f1872d7d83d670": {
-      "status": "confirmed"
-    },
-    "0x54926f8470fdaf30c1818f4d2b20463e90097e99059f7620811c8f78de298cb8": {
-      "status": "confirmed"
-    }
-  },
-  "contracts": {
-    "OwnerModule": {
-      "deployedAddress": "0x2Aa90f81C97e1E2b124c02257931599b1B923156",
-      "deployTransaction": "0xee37a84183f5f514aadb09a2d4d7f1dca435845f138c041a8df8fb215b8be1fd",
-      "deployedBytecodeHash": "0x395794c901029add8b19a33d96aaebf0f1e53f2f450629e035c440adfb3b7475",
-      "sourceName": "contracts/modules/OwnerModule.sol",
-      "isModule": true
-    },
-    "SNXTokenModule": {
-      "deployedAddress": "0x4C79561E16e0dA0370aB8F1C513967a048dBd702",
-      "deployTransaction": "0xc0ef9eff7520641e678178541af840b458010af7f5049485b643f4afc9c18736",
-      "deployedBytecodeHash": "0x747c0c0357af2c019397a7f6007a2a2b72b0340e8d9170afca26352f73c4813e",
-      "sourceName": "contracts/modules/SNXTokenModule.sol",
-      "isModule": true
-    },
-    "SynthsModule": {
-      "deployedAddress": "0x01Fe10Cc84d771f05a565b26EB75B5854e3136c2",
-      "deployTransaction": "0xba7b7d147e921293d78ec566ac0d2320e25045a93b5cbd8b461a1fe496cd148d",
-      "deployedBytecodeHash": "0xdc7359b0657924e77165923db5d290216377d571e4b9a0475591d62acfc4d3a5",
-      "sourceName": "contracts/modules/SynthsModule.sol",
-      "isModule": true
-    },
-    "UpgradeModule": {
-      "deployedAddress": "0xfE10E35e0D7a22f2E26840e626B225BF201Fc3a9",
-      "deployTransaction": "0x00b0eda8b8a9e81dc3775707630756bdb913ecbe2d9e711dadd8016f2c4e830d",
-      "deployedBytecodeHash": "0x1bdef1b3a6f21ed175c5509f8af7d09910ab308a22f34396805d22b5b536b885",
-      "sourceName": "contracts/modules/UpgradeModule.sol",
-      "isModule": true
-    },
-    "Router": {
-      "deployedAddress": "0x5b0921723CB4E1256d727B72299dDcdD9590dA7E",
-      "deployTransaction": "0x38c4bc09f33a2dd9318b5349ad770fee0fb678134dfaf03e60f1872d7d83d670",
-      "deployedBytecodeHash": "0x4147ffdc4e27d6018ec430f5eda6c8a35a46a9ea0599c81189ef6c95013bb79c",
-      "sourceName": "contracts/Router.sol"
-    },
-    "Proxy": {
-      "deployedAddress": "0x141f6ed94C0F8e1Ad30b8b1E0d0f23BF4709e535",
-      "deployTransaction": "0x54926f8470fdaf30c1818f4d2b20463e90097e99059f7620811c8f78de298cb8",
-      "deployedBytecodeHash": "0x6d898ca303a258c5723b87a08dcadd5b8de848327dd7b2213ce7e4ca63abccc2",
-      "sourceName": "contracts/Proxy.sol"
-    }
-  }
-}
\ No newline at end of file
```

### packages/synthetix-main/deployments/kovan/official/2021-11-25-00.json
```diff
@@ -0,0 +1,68 @@
+{
+  "properties": {
+    "completed": true,
+    "totalGasUsed": "3038469"
+  },
+  "transactions": {
+    "0x84e32875548e7890f98c932cec7aab8045a35d7c4b19c2e754273b4589168d25": {
+      "status": "confirmed"
+    },
+    "0x4d3570740a5fc660032b654a832ca64af21e4cee52b3ca4fd3bbd5a7f5594156": {
+      "status": "confirmed"
+    },
+    "0x48edf3a993d8651fa4b5194aa1731f8da7e39de37fe6ff83d0b57ea2f321e366": {
+      "status": "confirmed"
+    },
+    "0xa72d4f791a40bf22fa1b60de3e29a6bc0e51089767eb69e4e7dd613935aa0407": {
+      "status": "confirmed"
+    },
+    "0x3301104fac6acab63f6bd588003656b5df873aaa669c49ef0e19833673f2dea6": {
+      "status": "confirmed"
+    },
+    "0xa856eeacaf6d3fb0971520a541e31585b2d6da34d29fe9ff0d3904251bb8ad54": {
+      "status": "confirmed"
+    }
+  },
+  "contracts": {
+    "OwnerModule": {
+      "deployedAddress": "0x3fE920871a35d793aDA4416a82693140479E2146",
+      "deployTransaction": "0x84e32875548e7890f98c932cec7aab8045a35d7c4b19c2e754273b4589168d25",
+      "deployedBytecodeHash": "0xa2935553942dc8bacbbd9d70b2e46ecd7f5e4418c027f9fb99408380adf7ccef",
+      "sourceName": "contracts/modules/OwnerModule.sol",
+      "isModule": true
+    },
+    "SNXTokenModule": {
+      "deployedAddress": "0x294bF522247C42698fd40CB2b27191C6e66Ef64E",
+      "deployTransaction": "0x4d3570740a5fc660032b654a832ca64af21e4cee52b3ca4fd3bbd5a7f5594156",
+      "deployedBytecodeHash": "0x2d70743782aee9b32ce3f488c815cb3638f004a0fdd520adbbe7b3f6a999bfe6",
+      "sourceName": "contracts/modules/SNXTokenModule.sol",
+      "isModule": true
+    },
+    "SynthsModule": {
+      "deployedAddress": "0xeF264C24d4aE56c85F65210112a3f81329E6eAd8",
+      "deployTransaction": "0x48edf3a993d8651fa4b5194aa1731f8da7e39de37fe6ff83d0b57ea2f321e366",
+      "deployedBytecodeHash": "0x803dd932a7b30d3a3279e1e7f19a8556c066f4c6cebd288bd89352054943f303",
+      "sourceName": "contracts/modules/SynthsModule.sol",
+      "isModule": true
+    },
+    "UpgradeModule": {
+      "deployedAddress": "0x124dF771843984Fe4117f7906bCe28a324254418",
+      "deployTransaction": "0xa72d4f791a40bf22fa1b60de3e29a6bc0e51089767eb69e4e7dd613935aa0407",
+      "deployedBytecodeHash": "0x9b898392471e4acabd91f0f2e9d1f592298bece32ab1afa8cf6c70372a7bcd90",
+      "sourceName": "contracts/modules/UpgradeModule.sol",
+      "isModule": true
+    },
+    "Synthetix": {
+      "deployedAddress": "0x1f312D59cE0cc602b55f910b904dB135113b8bcA",
+      "deployTransaction": "0xa856eeacaf6d3fb0971520a541e31585b2d6da34d29fe9ff0d3904251bb8ad54",
+      "deployedBytecodeHash": "0xe623fef9888e5b0e133f275124f7ce6420c5a041f25938498a74de39db574ab7",
+      "sourceName": "contracts/Synthetix.sol"
+    },
+    "Router": {
+      "deployedAddress": "0x3861A1e38D8A70ebc09B0e95F16E63c77F7E2Cd9",
+      "deployTransaction": "0x3301104fac6acab63f6bd588003656b5df873aaa669c49ef0e19833673f2dea6",
+      "deployedBytecodeHash": "0x30bc38f7d378d445b4c628d86fe8bfb0bc5cc1f1bfdac8a48108ef35de3a4eac",
+      "sourceName": "contracts/Router.sol"
+    }
+  }
+}
\ No newline at end of file
```

### packages/synthetix-main/deployments/kovan/official/extended/2021-11-25-00.abis.json
```diff
@@ -201,12 +201,12 @@
   "SynthsModule": [
     {
       "inputs": [],
-      "name": "BeaconAlreadyDeployed",
+      "name": "BeaconAlreadyCreated",
       "type": "error"
     },
     {
       "inputs": [],
-      "name": "BeaconNotDeployed",
+      "name": "BeaconNotCreated",
       "type": "error"
     },
     {
@@ -221,7 +221,7 @@
     },
     {
       "inputs": [],
-      "name": "SynthAlreadyDeployed",
+      "name": "SynthAlreadyCreated",
       "type": "error"
     },
     {
@@ -234,7 +234,7 @@
           "type": "address"
         }
       ],
-      "name": "BeaconDeployed",
+      "name": "BeaconCreated",
       "type": "event"
     },
     {
@@ -253,12 +253,12 @@
           "type": "address"
         }
       ],
-      "name": "SynthDeployed",
+      "name": "SynthCreated",
       "type": "event"
     },
     {
       "inputs": [],
-      "name": "deployBeacon",
+      "name": "createBeacon",
       "outputs": [],
       "stateMutability": "nonpayable",
       "type": "function"
@@ -269,9 +269,24 @@
           "internalType": "bytes32",
           "name": "synth",
           "type": "bytes32"
+        },
+        {
+          "internalType": "string",
+          "name": "synthName",
+          "type": "string"
+        },
+        {
+          "internalType": "string",
+          "name": "synthSymbol",
+          "type": "string"
+        },
+        {
+          "internalType": "uint8",
+          "name": "synthDecimals",
+          "type": "uint8"
         }
       ],
-      "name": "deploySynth",
+      "name": "createSynth",
       "outputs": [],
       "stateMutability": "nonpayable",
       "type": "function"
@@ -432,42 +447,42 @@
       "type": "function"
     }
   ],
-  "Router": [
+  "Synthetix": [
     {
       "inputs": [
         {
-          "internalType": "bytes4",
-          "name": "sel",
-          "type": "bytes4"
+          "internalType": "address",
+          "name": "firstImplementation",
+          "type": "address"
         }
       ],
-      "name": "UnknownSelector",
-      "type": "error"
+      "stateMutability": "nonpayable",
+      "type": "constructor"
     },
     {
       "stateMutability": "payable",
       "type": "fallback"
+    },
+    {
+      "stateMutability": "payable",
+      "type": "receive"
     }
   ],
-  "Proxy": [
+  "Router": [
     {
       "inputs": [
         {
-          "internalType": "address",
-          "name": "firstImplementation",
-          "type": "address"
+          "internalType": "bytes4",
+          "name": "sel",
+          "type": "bytes4"
         }
       ],
-      "stateMutability": "nonpayable",
-      "type": "constructor"
+      "name": "UnknownSelector",
+      "type": "error"
     },
     {
       "stateMutability": "payable",
       "type": "fallback"
-    },
-    {
-      "stateMutability": "payable",
-      "type": "receive"
     }
   ]
 }
\ No newline at end of file
```

### packages/synthetix-main/hardhat.config.js
```diff
@@ -5,7 +5,15 @@ require('@nomiclabs/hardhat-ethers');
 require('@synthetixio/deployer');
 
 module.exports = {
-  solidity: '0.8.4',
+  solidity: {
+    version: '0.8.7',
+    settings: {
+      optimizer: {
+        enabled: true,
+        runs: 200,
+      },
+    },
+  },
   networks: {
     local: {
       url: 'http://localhost:8545',
```
