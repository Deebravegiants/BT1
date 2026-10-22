# [?] Fix base bridging and a race condition in key funder (#3012)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2023-12-01
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/9fc0866b29bf2190ecb8bc0ba78c267987c4f809
Type: security-commit

## Details
Fix base bridging and a race condition in key funder (#3012)

### Description

Turns out bridging from L1 to Base has been broken the whole time :(
it's because the version of @eth-optimism/sdk we were using was 1.8.0
(according to yarn.lock) which was released in late 2022
https://github.com/ethereum-optimism/optimism/releases/tag/%40eth-optimism%2Fsdk%401.8.0,
far before Base was launched. So we'd always get this error in key
funder because we rely on the optimism SDK knowing about Base's chain
ID:
```
{"chain":"base","error":"Error: cannot get contract AddressManager for unknown L2 chain ID 8453, you must provide an address\n    at getOEContract (/hyperlane-monorepo/node_modules/@eth-optimism/sdk/src/utils/contracts.ts:58:11)\n    at getAllOEContracts (/hyperlane-monorepo/node_modules/@eth-optimism/sdk/src/utils/contracts.ts:121:46)\n    at new CrossChainMessenger (/hyperlane-monorepo/node_modules/@eth-optimism/sdk/src/cross-chain-messenger.ts:170:39)\n    at ContextFunder.bridgeToOptimism (/hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:652:33)\n    at ContextFunder.bridgeToL2 (/hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:637:23)\n    at processTicksAndRejections (node:internal/process/task_queues:96:5)\n    at async ContextFunder.bridgeIfL2 (/hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:492:9)\n    at async gracefullyHandleError (/hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:774:5)\n    at async /hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:394:29\n    at async Promise.all (index 9)","level":"error","message":"Error bridging to L2"}
```

The fix was just to upgrade to a newer optimism SDK version

A mystery to me is that we'd get that log ^ but sometimes the key funder
pod would show as having ran successfully. My best guess here is there
was a race condition in `fund` when we had a variable local to the
function called `failureOccurred` that many promises which were
`Promise.all`'d would read and write to it via `failureOccurred ||=
await someFallibleFn()`. I changed the logic here to not have multiple
concurrent promises contend for the variable

Also made a small change to not include mantapacific in the list of
relayer keys for the Hyperlane context. It's not ever used, and had a
downstream effect of us trying to fund the Kathy key on mantapacific,
which we don't want to actually do

### Drive-by changes

n/a

### Related issues

n/a

### Backward compatibility

ye

### Testing

ran locally

### typescript/infra/config/environments/mainnet3/chains.ts
```diff
@@ -65,14 +65,17 @@ export const ethereumChainNames = Object.keys(
   ethereumMainnetConfigs,
 ) as MainnetChains[];
 
+// Remove mantapacific, as it's not considered a "blessed"
+// chain. It's not included in the scraper domains table,
+// and we don't relay to mantapacific on the Hyperlane or RC contexts.
+const hyperlaneContextRelayChains = ethereumChainNames.filter(
+  (chainName) => chainName !== chainMetadata.mantapacific.name,
+);
+
 // Hyperlane & RC context agent chain names.
 export const agentChainNames: AgentChainNames = {
   // Run validators for all chains.
   [Role.Validator]: supportedChainNames,
-  // Only run relayers for Ethereum chains at the moment.
-  [Role.Relayer]: ethereumChainNames,
-  // Remove mantapacific for now, as it's not included in the scraper domains table
-  [Role.Scraper]: ethereumChainNames.filter(
-    (chainName) => chainName !== chainMetadata.mantapacific.name,
-  ),
+  [Role.Relayer]: hyperlaneContextRelayChains,
+  [Role.Scraper]: hyperlaneContextRelayChains,
 };
```

### typescript/infra/package.json
```diff
@@ -8,7 +8,7 @@
     "@aws-sdk/client-kms": "3.48.0",
     "@aws-sdk/client-s3": "^3.74.0",
     "@cosmjs/amino": "^0.31.3",
-    "@eth-optimism/sdk": "^1.7.0",
+    "@eth-optimism/sdk": "^3.1.6",
     "@ethersproject/experimental": "^5.7.0",
     "@ethersproject/hardware-wallets": "^5.7.0",
     "@ethersproject/providers": "^5.7.2",
```

### typescript/infra/scripts/funding/fund-keys-from-deployer.ts
```diff
@@ -395,10 +395,10 @@ class ContextFunder {
   // Funds all the roles in this.rolesToFund
   // Returns whether a failure occurred.
   async fund(): Promise<boolean> {
-    let failureOccurred = false;
-
     const chainKeys = this.getChainKeys();
-    const promises = Object.entries(chainKeys).map(async ([chain, keys]) => {
+    const chainKeyEntries = Object.entries(chainKeys);
+    const promises = chainKeyEntries.map(async ([chain, keys]) => {
+      let failureOccurred = false;
       if (keys.length > 0) {
         if (!this.skipIgpClaim) {
           failureOccurred ||= await gracefullyHandleError(
@@ -418,14 +418,25 @@ class ContextFunder {
         const failure = await this.attemptToFundKey(key, chain);
         failureOccurred ||= failure;
       }
+      return failureOccurred;
     });
 
-    try {
-      await Promise.all(promises);
-    } catch (e) {
-      error('Unhandled error when funding key', { error: format(e) });
-      failureOccurred = true;
-    }
+    // A failure occurred if any of the promises rejected or
+    // if any of them resolved with true, indicating a failure
+    // somewhere along the way
+    const failureOccurred = (await Promise.allSettled(promises)).reduce(
+      (failureAgg, result, i) => {
+        if (result.status === 'rejected') {
+          error('Funding promise for chain rejected', {
+            chain: chainKeyEntries[i][0],
+            error: format(result.reason),
+          });
+          return true;
+        }
+        return result.value || failureAgg;
+      },
+      false,
+    );
 
     return failureOccurred;
   }
```

### yarn.lock
```diff
@@ -3191,33 +3191,14 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@eth-optimism/contracts-bedrock@npm:0.11.0":
-  version: 0.11.0
-  resolution: "@eth-optimism/contracts-bedrock@npm:0.11.0"
-  dependencies:
-    "@eth-optimism/core-utils": "npm:^0.12.0"
-    "@openzeppelin/contracts": "npm:4.7.3"
-    "@openzeppelin/contracts-upgradeable": "npm:4.7.3"
-    ethers: "npm:^5.7.0"
-    hardhat: "npm:^2.9.6"
-  checksum: 26f2bf2fbaddc20c6f04f03855c9aecb569f0492c87be45e55a845659461332c7d2d0caa9fea8e3d3c6e4b612320388bfcca64c3bf106893417619addb6045fd
-  languageName: node
-  linkType: hard
-
-"@eth-optimism/contracts@npm:0.5.39":
-  version: 0.5.39
-  resolution: "@eth-optimism/contracts@npm:0.5.39"
-  dependencies:
-    "@eth-optimism/core-utils": "npm:0.12.0"
-    "@ethersproject/abstract-provider": "npm:^5.7.0"
-    "@ethersproject/abstract-signer": "npm:^5.7.0"
-  peerDependencies:
-    ethers: ^5
-  checksum: 941c254f5b101620afa38b23f315fbee9bae74be092f6571aa516662340b739bf504b38c4edadaafecf515d4bb0e4c84bf1b647f16b14f03c447e6c584025554
+"@eth-optimism/contracts-bedrock@npm:0.16.2":
+  version: 0.16.2
+  resolution: "@eth-optimism/contracts-bedrock@npm:0.16.2"
+  checksum: 4708a5f0385e784c23bb40bc0c4321bac3ccc469ccba4491bb8ffbee267755bad5929215d1af923b372edb93f40bd8fb04d9a1e6caa4fb615776099d23688b9b
   languageName: node
   linkType: hard
 
-"@eth-optimism/contracts@npm:^0.6.0":
+"@eth-optimism/contracts@npm:0.6.0, @eth-optimism/contracts@npm:^0.6.0":
   version: 0.6.0
   resolution: "@eth-optimism/contracts@npm:0.6.0"
   dependencies:
@@ -3230,7 +3211,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@eth-optimism/core-utils@npm:0.12.0, @eth-optimism/core-utils@npm:^0.12.0":
+"@eth-optimism/core-utils@npm:0.12.0":
   version: 0.12.0
   resolution: "@eth-optimism/core-utils@npm:0.12.0"
   dependencies:
@@ -3254,19 +3235,41 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@eth-optimism/sdk@npm:^1.7.0":
-  version: 1.8.0
-  resolution: "@eth-optimism/sdk@npm:1.8.0"
+"@eth-optimism/core-utils@npm:0.13.1":
+  version: 0.13.1
+  resolution: "@eth-optimism/core-utils@npm:0.13.1"
   dependencies:
-    "@eth-optimism/contracts": "npm:0.5.39"
-    "@eth-optimism/contracts-bedrock": "npm:0.11.0"
-    "@eth-optimism/core-utils": "npm:0.12.0"
+    "@ethersproject/abi": "npm:^5.7.0"
+    "@ethersproject/abstract-provider": "npm:^5.7.0"
+    "@ethersproject/address": "npm:^5.7.0"
+    "@ethersproject/bignumber": "npm:^5.7.0"
+    "@ethersproject/bytes": "npm:^5.7.0"
+    "@ethersproject/constants": "npm:^5.7.0"
+    "@ethersproject/contracts": "npm:^5.7.0"
+    "@ethersproject/keccak256": "npm:^5.7.0"
+    "@ethersproject/properties": "npm:^5.7.0"
+    "@ethersproject/rlp": "npm:^5.7.0"
+    "@ethersproject/web": "npm:^5.7.1"
+    chai: "npm:^4.3.9"
+    ethers: "npm:^5.7.2"
+    node-fetch: "npm:^2.6.7"
+  checksum: 7d9a3b94d05c3becce24562003032d6d2ddc4396e6420152ee3ad287a614ca513c53d43ecaeba5e238abb8bd85c352a42854a0f949df19cfb0219fc441e2da09
+  languageName: node
+  linkType: hard
+
+"@eth-optimism/sdk@npm:^3.1.6":
+  version: 3.1.6
+  resolution: "@eth-optimism/sdk@npm:3.1.6"
+  dependencies:
+    "@eth-optimism/contracts": "npm:0.6.0"
+    "@eth-optimism/contracts-bedrock": "npm:0.16.2"
+    "@eth-optimism/core-utils": "npm:0.13.1"
     lodash: "npm:^4.17.21"
-    merkletreejs: "npm:^0.2.27"
+    merkletreejs: "npm:^0.3.11"
     rlp: "npm:^2.2.7"
   peerDependencies:
     ethers: ^5
-  checksum: 179bb561d30caca0f17affc8012fb4fd1ab30a566651f197111f3ad450f7decbf7ff212ba526ed95f02528694ff095d6e814bf642075a4e99c0e6de8dc322751
+  checksum: 39ab8b94c7a4c4333ed31046de5a429529486b287a8080f7ad9f1a2d4c51d5f09a545931501c1b930578baca58cfc072626c460570b4bb6ba304f08061cb6f72
   languageName: node
   linkType: hard
 
@@ -4068,7 +4071,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@ethersproject/web@npm:5.7.1":
+"@ethersproject/web@npm:5.7.1, @ethersproject/web@npm:^5.7.1":
   version: 5.7.1
   resolution: "@ethersproject/web@npm:5.7.1"
   dependencies:
@@ -4336,7 +4339,7 @@ __metadata:
     "@aws-sdk/client-kms": "npm:3.48.0"
     "@aws-sdk/client-s3": "npm:^3.74.0"
     "@cosmjs/amino": "npm:^0.31.3"
-    "@eth-optimism/sdk": "npm:^1.7.0"
+    "@eth-optimism/sdk": "npm:^3.1.6"
     "@ethersproject/experimental": "npm:^5.7.0"
     "@ethersproject/hardware-wallets": "npm:^5.7.0"
     "@ethersproject/providers": "npm:^5.7.2"
@@ -4911,20 +4914,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-block@npm:^4.0.0":
-  version: 4.0.0
-  resolution: "@nomicfoundation/ethereumjs-block@npm:4.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-common": "npm:^3.0.0"
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-trie": "npm:^5.0.0"
-    "@nomicfoundation/ethereumjs-tx": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    ethereum-cryptography: "npm:0.1.3"
-  checksum: cbdd37fddeeb3aa29dd750409fc4ce1b3ef5691d45d4dc0808706e99080e6f3f4ee4b95e3ce14fccfb91296513196cea84095c64eb740f81ef38f3d9ab0d2a21
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-blockchain@npm:7.0.2":
   version: 7.0.2
   resolution: "@nomicfoundation/ethereumjs-blockchain@npm:7.0.2"
@@ -4946,26 +4935,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-blockchain@npm:^6.0.0":
-  version: 6.0.0
-  resolution: "@nomicfoundation/ethereumjs-blockchain@npm:6.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-block": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-common": "npm:^3.0.0"
-    "@nomicfoundation/ethereumjs-ethash": "npm:^2.0.0"
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-trie": "npm:^5.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    abstract-level: "npm:^1.0.3"
-    debug: "npm:^4.3.3"
-    ethereum-cryptography: "npm:0.1.3"
-    level: "npm:^8.0.0"
-    lru-cache: "npm:^5.1.1"
-    memory-level: "npm:^1.0.0"
-  checksum: c380735f69182576694b3ffd5eff7a5e8e562efb5cbd96e5cf186c68a0592acfb0effe4551cdf4ad366f831d4b7dd28c3347bee8ca845ae2352b8e36cdcbb6cb
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-common@npm:4.0.2":
   version: 4.0.2
   resolution: "@nomicfoundation/ethereumjs-common@npm:4.0.2"
@@ -4976,16 +4945,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-common@npm:^3.0.0":
-  version: 3.0.0
-  resolution: "@nomicfoundation/ethereumjs-common@npm:3.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    crc-32: "npm:^1.2.0"
-  checksum: d7012b0d05fba75e6ad2f54e60f777231896377a0a369af22d4868e4e260fb7e2586ac8d51c35b56ea2c1fa2e62dfef8669b653ed3e3b7816cfc38f2acf26090
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-ethash@npm:3.0.2":
   version: 3.0.2
   resolution: "@nomicfoundation/ethereumjs-ethash@npm:3.0.2"
@@ -5000,20 +4959,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-ethash@npm:^2.0.0":
-  version: 2.0.0
-  resolution: "@nomicfoundation/ethereumjs-ethash@npm:2.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-block": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    abstract-level: "npm:^1.0.3"
-    bigint-crypto-utils: "npm:^3.0.23"
-    ethereum-cryptography: "npm:0.1.3"
-  checksum: dcabac814b7496a19824f6048157a095713afcb0676f4dd3d6172e579b31789dccd0f4417847c1901af3092be0021cc3e98f7f770a81766f505da93ff5930b00
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-evm@npm:2.0.2":
   version: 2.0.2
   resolution: "@nomicfoundation/ethereumjs-evm@npm:2.0.2"
@@ -5030,22 +4975,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-evm@npm:^1.0.0":
-  version: 1.0.0
-  resolution: "@nomicfoundation/ethereumjs-evm@npm:1.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-common": "npm:^3.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    "@types/async-eventemitter": "npm:^0.2.1"
-    async-eventemitter: "npm:^0.2.4"
-    debug: "npm:^4.3.3"
-    ethereum-cryptography: "npm:0.1.3"
-    mcl-wasm: "npm:^0.7.1"
-    rustbn.js: "npm:~0.2.0"
-  checksum: 5a86ded335d74e63564d0b012c2e7807a1f8c9a2aca65a152fab5eb8200b7d2f23bc9fc31e26a3403a76eaba37ccf1bae4be81310da5e4619f8e1d63f1d0e3fd
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-rlp@npm:5.0.2":
   version: 5.0.2
   resolution: "@nomicfoundation/ethereumjs-rlp@npm:5.0.2"
@@ -5055,15 +4984,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-rlp@npm:^4.0.0, @nomicfoundation/ethereumjs-rlp@npm:^4.0.0-beta.2":
-  version: 4.0.0
-  resolution: "@nomicfoundation/ethereumjs-rlp@npm:4.0.0"
-  bin:
-    rlp: bin/rlp
-  checksum: 9e3e52876e408583cf3b19fd65979162eded9e1d02b699d4936a53bfba4155713084d0b37dbc938ec6a34e5bef61b9f2e3682684a86c6a29ea3900ac51113e92
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-statemanager@npm:2.0.2":
   version: 2.0.2
   resolution: "@nomicfoundation/ethereumjs-statemanager@npm:2.0.2"
@@ -5078,21 +4998,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-statemanager@npm:^1.0.0":
-  version: 1.0.0
-  resolution: "@nomicfoundation/ethereumjs-statemanager@npm:1.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-common": "npm:^3.0.0"
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-trie": "npm:^5.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    debug: "npm:^4.3.3"
-    ethereum-cryptography: "npm:0.1.3"
-    functional-red-black-tree: "npm:^1.0.1"
-  checksum: faf7629ec3b5b494a955c9ab7a2e775c01796ad6b2441d10562407056b6a6e06ff751ac03ea131c3eddedc12189f1ae382be0cf2854fdce17f28ce62eb3c2f42
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-trie@npm:6.0.2":
   version: 6.0.2
   resolution: "@nomicfoundation/ethereumjs-trie@npm:6.0.2"
@@ -5106,18 +5011,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-trie@npm:^5.0.0":
-  version: 5.0.0
-  resolution: "@nomicfoundation/ethereumjs-trie@npm:5.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    ethereum-cryptography: "npm:0.1.3"
-    readable-stream: "npm:^3.6.0"
-  checksum: 709cfbb7be2c64208a3e712c27f0bc0580fc723d12340b211353beeddb886f68059170d51529650a090b821b6a21dbf63dc67499f23877e377fbc97295254b12
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-tx@npm:5.0.2":
   version: 5.0.2
   resolution: "@nomicfoundation/ethereumjs-tx@npm:5.0.2"
@@ -5132,18 +5025,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-tx@npm:^4.0.0":
-  version: 4.0.0
-  resolution: "@nomicfoundation/ethereumjs-tx@npm:4.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-common": "npm:^3.0.0"
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    ethereum-cryptography: "npm:0.1.3"
-  checksum: 0833c6a4bfe5ad77a2931710ebe79d972d8e89eb59c9066bb0c7347cd6135a66bf0901c55e8c84827c1edad9200446ef0e5260a6026630552c9828e7f4f123a1
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-util@npm:9.0.2":
   version: 9.0.2
   resolution: "@nomicfoundation/ethereumjs-util@npm:9.0.2"
@@ -5155,16 +5036,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-util@npm:^8.0.0":
-  version: 8.0.0
-  resolution: "@nomicfoundation/ethereumjs-util@npm:8.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0-beta.2"
-    ethereum-cryptography: "npm:0.1.3"
-  checksum: 8da64af39b83750347bf73fb30b169e1bf702cc26d6f94434a78521b569af9ebbd5c23d729e5e1ce38b22e354696af83f823bccc95f8a427c1baf722936d5404
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/ethereumjs-vm@npm:7.0.2":
   version: 7.0.2
   resolution: "@nomicfoundation/ethereumjs-vm@npm:7.0.2"
@@ -5186,30 +5057,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@nomicfoundation/ethereumjs-vm@npm:^6.0.0":
-  version: 6.0.0
-  resolution: "@nomicfoundation/ethereumjs-vm@npm:6.0.0"
-  dependencies:
-    "@nomicfoundation/ethereumjs-block": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-blockchain": "npm:^6.0.0"
-    "@nomicfoundation/ethereumjs-common": "npm:^3.0.0"
-    "@nomicfoundation/ethereumjs-evm": "npm:^1.0.0"
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-statemanager": "npm:^1.0.0"
-    "@nomicfoundation/ethereumjs-trie": "npm:^5.0.0"
-    "@nomicfoundation/ethereumjs-tx": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    "@types/async-eventemitter": "npm:^0.2.1"
-    async-eventemitter: "npm:^0.2.4"
-    debug: "npm:^4.3.3"
-    ethereum-cryptography: "npm:0.1.3"
-    functional-red-black-tree: "npm:^1.0.1"
-    mcl-wasm: "npm:^0.7.1"
-    rustbn.js: "npm:~0.2.0"
-  checksum: 16c34baef9a8561d6d580164f258f03d8e0573b76cabb2373835e30ee684aef70d121c4d3a73f3fa5e82081a8b81f643326d11861b18f36d9dcf8e7cf157be96
-  languageName: node
-  linkType: hard
-
 "@nomicfoundation/solidity-analyzer-darwin-arm64@npm:0.1.0":
   version: 0.1.0
   resolution: "@nomicfoundation/solidity-analyzer-darwin-arm64@npm:0.1.0"
@@ -5382,27 +5229,13 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@openzeppelin/contracts-upgradeable@npm:4.7.3":
-  version: 4.7.3
-  resolution: "@openzeppelin/contracts-upgradeable@npm:4.7.3"
-  checksum: 7c72ffeca867478b5aa8e8c7adb3d1ce114cfdc797ed4f3cd074788cf4da25d620ffffd624ac7e9d1223eecffeea9f7b79200ff70dc464cc828c470ccd12ddf1
-  languageName: node
-  linkType: hard
-
 "@openzeppelin/contracts-upgradeable@npm:^4.9.3, @openzeppelin/contracts-upgradeable@npm:^v4.9.3":
   version: 4.9.3
   resolution: "@openzeppelin/contracts-upgradeable@npm:4.9.3"
   checksum: d8fd6fd9d2271fbdd3958c20769b72a241687883ecd3bea05a3969568cdcabdee9d53c21ac776a651c397507d9c22d8db0a4fb970d27bdab918979fae7285a2f
   languageName: node
   linkType: hard
 
-"@openzeppelin/contracts@npm:4.7.3":
-  version: 4.7.3
-  resolution: "@openzeppelin/contracts@npm:4.7.3"
-  checksum: 3d16ed8943938373ecc331c2ab83c3e8d0d89aed0c2a109aaa61ca6524b4c31cb5a81185c6f93ce9ee2dda685a4328fd85bd217929ae598f4be813d5d4cd1b78
-  languageName: node
-  linkType: hard
-
 "@openzeppelin/contracts@npm:^4.9.3":
   version: 4.9.3
   resolution: "@openzeppelin/contracts@npm:4.9.3"
@@ -6015,13 +5848,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@types/async-eventemitter@npm:^0.2.1":
-  version: 0.2.1
-  resolution: "@types/async-eventemitter@npm:0.2.1"
-  checksum: 52f6a9c6773edec9bc8449273de8b08fca45ebbf1907c755cd67be9aca4f26988aebb6d0e461aecf01463b76f0e1b427f149a8ce54d27cec191702488c676f48
-  languageName: node
-  linkType: hard
-
 "@types/bn.js@npm:^4.11.3":
   version: 4.11.6
   resolution: "@types/bn.js@npm:4.11.6"
@@ -6670,15 +6496,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"abort-controller@npm:^3.0.0":
-  version: 3.0.0
-  resolution: "abort-controller@npm:3.0.0"
-  dependencies:
-    event-target-shim: "npm:^5.0.0"
-  checksum: ed84af329f1828327798229578b4fe03a4dd2596ba304083ebd2252666bdc1d7647d66d0b18704477e1f8aa315f055944aa6e859afebd341f12d0a53c37b4b40
-  languageName: node
-  linkType: hard
-
 "abortcontroller-polyfill@npm:^1.7.3":
   version: 1.7.3
   resolution: "abortcontroller-polyfill@npm:1.7.3"
@@ -7892,6 +7709,21 @@ __metadata:
   languageName: node
   linkType: hard
 
+"chai@npm:^4.3.9":
+  version: 4.3.10
+  resolution: "chai@npm:4.3.10"
+  dependencies:
+    assertion-error: "npm:^1.1.0"
+    check-error: "npm:^1.0.3"
+    deep-eql: "npm:^4.1.3"
+    get-func-name: "npm:^2.0.2"
+    loupe: "npm:^2.3.6"
+    pathval: "npm:^1.1.1"
+    type-detect: "npm:^4.0.8"
+  checksum: 9e545fd60f5efee4f06f7ad62f7b1b142932b08fbb3454db69defd511e7c58771ce51843764212da1e129b2c9d1b029fbf5f98da030fe67a95a0853e8679524f
+  languageName: node
+  linkType: hard
+
 "chalk@npm:^2.0.0, chalk@npm:^2.1.0, chalk@npm:^2.4.1, chalk@npm:^2.4.2":
   version: 2.4.2
   resolution: "chalk@npm:2.4.2"
@@ -7941,6 +7773,15 @@ __metadata:
   languageName: node
   linkType: hard
 
+"check-error@npm:^1.0.3":
+  version: 1.0.3
+  resolution: "check-error@npm:1.0.3"
+  dependencies:
+    get-func-name: "npm:^2.0.2"
+  checksum: e2131025cf059b21080f4813e55b3c480419256914601750b0fee3bd9b2b8315b531e551ef12560419b8b6d92a3636511322752b1ce905703239e7cc451b6399
+  languageName: node
+  linkType: hard
+
 "chokidar@npm:3.3.0":
   version: 3.3.0
   resolution: "chokidar@npm:3.3.0"
@@ -8549,10 +8390,10 @@ __metadata:
   languageName: node
   linkType: hard
 
-"crypto-js@npm:^3.1.9-1":
-  version: 3.3.0
-  resolution: "crypto-js@npm:3.3.0"
-  checksum: d7e11f3a387fb143be834e1a25ecf57ead6f5765e90fbf3aed9cead680cc38b1d241718768b7bfec448a843f569374ea5b5870ac7a8165e4bfa1915f0b00c89c
+"crypto-js@npm:^4.2.0":
+  version: 4.2.0
+  resolution: "crypto-js@npm:4.2.0"
+  checksum: c7bcc56a6e01c3c397e95aa4a74e4241321f04677f9a618a8f48a63b5781617248afb9adb0629824792e7ec20ca0d4241a49b6b2938ae6f973ec4efc5c53c924
   languageName: node
   linkType: hard
 
@@ -8721,6 +8562,15 @@ __metadata:
   languageName: node
   linkType: hard
 
+"deep-eql@npm:^4.1.3":
+  version: 4.1.3
+  resolution: "deep-eql@npm:4.1.3"
+  dependencies:
+    type-detect: "npm:^4.0.0"
+  checksum: 12ce93ae63de187e77b076d3d51bfc28b11f98910a22c18714cce112791195e86a94f97788180994614b14562a86c9763f67c69f785e4586f806b5df39bf9301
+  languageName: node
+  linkType: hard
+
 "deep-extend@npm:^0.6.0, deep-extend@npm:~0.6.0":
   version: 0.6.0
   resolution: "deep-extend@npm:0.6.0"
@@ -9734,13 +9584,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"event-target-shim@npm:^5.0.0":
-  version: 5.0.1
-  resolution: "event-target-shim@npm:5.0.1"
-  checksum: 49ff46c3a7facbad3decb31f597063e761785d7fdb3920d4989d7b08c97a61c2f51183e2f3a03130c9088df88d4b489b1b79ab632219901f184f85158508f4c8
-  languageName: node
-  linkType: hard
-
 "eventemitter3@npm:4.0.4":
   version: 4.0.4
   resolution: "eventemitter3@npm:4.0.4"
@@ -10466,6 +10309,13 @@ __metadata:
   languageName: node
   linkType: hard
 
+"get-func-name@npm:^2.0.1, get-func-name@npm:^2.0.2":
+  version: 2.0.2
+  resolution: "get-func-name@npm:2.0.2"
+  checksum: 3f62f4c23647de9d46e6f76d2b3eafe58933a9b3830c60669e4180d6c601ce1b4aa310ba8366143f55e52b139f992087a9f0647274e8745621fa2af7e0acf13b
+  languageName: node
+  linkType: hard
+
 "get-intrinsic@npm:^1.0.2, get-intrinsic@npm:^1.1.0, get-intrinsic@npm:^1.1.1":
   version: 1.1.2
   resolution: "get-intrinsic@npm:1.1.2"
@@ -10982,74 +10832,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"hardhat@npm:^2.9.6":
-  version: 2.12.4
-  resolution: "hardhat@npm:2.12.4"
-  dependencies:
-    "@ethersproject/abi": "npm:^5.1.2"
-    "@metamask/eth-sig-util": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-block": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-blockchain": "npm:^6.0.0"
-    "@nomicfoundation/ethereumjs-common": "npm:^3.0.0"
-    "@nomicfoundation/ethereumjs-evm": "npm:^1.0.0"
-    "@nomicfoundation/ethereumjs-rlp": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-statemanager": "npm:^1.0.0"
-    "@nomicfoundation/ethereumjs-trie": "npm:^5.0.0"
-    "@nomicfoundation/ethereumjs-tx": "npm:^4.0.0"
-    "@nomicfoundation/ethereumjs-util": "npm:^8.0.0"
-    "@nomicfoundation/ethereumjs-vm": "npm:^6.0.0"
-    "@nomicfoundation/solidity-analyzer": "npm:^0.1.0"
-    "@sentry/node": "npm:^5.18.1"
-    "@types/bn.js": "npm:^5.1.0"
-    "@types/lru-cache": "npm:^5.1.0"
-    abort-controller: "npm:^3.0.0"
-    adm-zip: "npm:^0.4.16"
-    aggregate-error: "npm:^3.0.0"
-    ansi-escapes: "npm:^4.3.0"
-    chalk: "npm:^2.4.2"
-    chokidar: "npm:^3.4.0"
-    ci-info: "npm:^2.0.0"
-    debug: "npm:^4.1.1"
-    enquirer: "npm:^2.3.0"
-    env-paths: "npm:^2.2.0"
-    ethereum-cryptography: "npm:^1.0.3"
-    ethereumjs-abi: "npm:^0.6.8"
-    find-up: "npm:^2.1.0"
-    fp-ts: "npm:1.19.3"
-    fs-extra: "npm:^7.0.1"
-    glob: "npm:7.2.0"
-    immutable: "npm:^4.0.0-rc.12"
-    io-ts: "npm:1.10.4"
-    keccak: "npm:^3.0.2"
-    lodash: "npm:^4.17.11"
-    mnemonist: "npm:^0.38.0"
-    mocha: "npm:^10.0.0"
-    p-map: "npm:^4.0.0"
-    qs: "npm:^6.7.0"
-    raw-body: "npm:^2.4.1"
-    resolve: "npm:1.17.0"
-    semver: "npm:^6.3.0"
-    solc: "npm:0.7.3"
-    source-map-support: "npm:^0.5.13"
-    stacktrace-parser: "npm:^0.1.10"
-    tsort: "npm:0.0.1"
-    undici: "npm:^5.4.0"
-    uuid: "npm:^8.3.2"
-    ws: "npm:^7.4.6"
-  peerDependencies:
-    ts-node: "*"
-    typescript: "*"
-  peerDependenciesMeta:
-    ts-node:
-      optional: true
-    typescript:
-      optional: true
-  bin:
-    hardhat: internal/cli/cli.js
-  checksum: c92dd697b105fc3a81de4a1061f44e95b2c06169afde4704d1cd26e038693c5c9869b9be219342cd1e243796b3119f583c776c65abfb2bf53ed0d3f3b27ed612
-  languageName: node
-  linkType: hard
-
 "has-bigints@npm:^1.0.1, has-bigints@npm:^1.0.2":
   version: 1.0.2
   resolution: "has-bigints@npm:1.0.2"
@@ -12669,6 +12451,15 @@ __metadata:
   languageName: node
   linkType: hard
 
+"loupe@npm:^2.3.6":
+  version: 2.3.7
+  resolution: "loupe@npm:2.3.7"
+  dependencies:
+    get-func-name: "npm:^2.0.1"
+  checksum: 635c8f0914c2ce7ecfe4e239fbaf0ce1d2c00e4246fafcc4ed000bfdb1b8f89d05db1a220054175cca631ebf3894872a26fffba0124477fcb562f78762848fb1
+  languageName: node
+  linkType: hard
+
 "lowercase-keys@npm:^1.0.0":
   version: 1.0.1
   resolution: "lowercase-keys@npm:1.0.1"
@@ -12902,16 +12693,16 @@ __metadata:
   languageName: node
   linkType: hard
 
-"merkletreejs@npm:^0.2.27":
-  version: 0.2.32
-  resolution: "merkletreejs@npm:0.2.32"
+"merkletreejs@npm:^0.3.11":
+  version: 0.3.11
+  resolution: "merkletreejs@npm:0.3.11"
   dependencies:
     bignumber.js: "npm:^9.0.1"
     buffer-reverse: "npm:^1.0.1"
-    crypto-js: "npm:^3.1.9-1"
+    crypto-js: "npm:^4.2.0"
     treeify: "npm:^1.1.0"
     web3-utils: "npm:^1.3.4"
-  checksum: 00c53a7fe9e87150b262b249f75c9e925641a628388d327f1b5fb4de9d146c95e58c67abe6771d5217b2555ebc3a9cc433ce958003f85dde58bda535225e853f
+  checksum: a93520ef768648d1e4ebd175182bd3d304270b8eb0700df5be99395fb3ad8805407bdaf3231d13b1649e87de799aa06d71c616db047ad039025764eb23b02244
   languageName: node
   linkType: hard
 
@@ -14605,7 +14396,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"qs@npm:^6.4.0, qs@npm:^6.7.0":
+"qs@npm:^6.4.0":
   version: 6.10.5
   resolution: "qs@npm:6.10.5"
   dependencies:
```
