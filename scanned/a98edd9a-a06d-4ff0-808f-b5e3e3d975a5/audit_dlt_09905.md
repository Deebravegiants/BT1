# [?] Fix crash with pool URL

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2022-03-08
Source: https://github.com/iron-fish/ironfish/commit/cd6a87017b7fe5c9ca1aad27219e1c5d4a2a8b6b
Type: security-commit

## Details
Fix crash with pool URL

## Patch
### ironfish-cli/src/commands/miners/start.ts
```diff
@@ -2,7 +2,13 @@
  * License, v. 2.0. If a copy of the MPL was not distributed with this
  * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
 import { Flags } from '@oclif/core'
-import { GraffitiUtils, isValidPublicAddress, MiningPoolMiner, MiningSoloMiner } from 'ironfish'
+import {
+  GraffitiUtils,
+  isValidPublicAddress,
+  MiningPoolMiner,
+  MiningSoloMiner,
+  parseUrl,
+} from 'ironfish'
 import os from 'os'
 import { IronfishCommand } from '../../command'
 import { RemoteFlags } from '../../flags'
@@ -57,7 +63,10 @@ export class Miner extends IronfishCommand {
         `Staring to mine with public address: ${flags.publicAddress} at pool ${flags.pool}`,
       )
 
-      const { hostname, port } = new URL(flags.pool)
+      let { hostname, port } = parseUrl(flags.pool)
+
+      hostname = hostname ?? 'localhost'
+      port = port ?? 1234
 
       const miner = new MiningPoolMiner({
         threadCount: flags.threads,
```
