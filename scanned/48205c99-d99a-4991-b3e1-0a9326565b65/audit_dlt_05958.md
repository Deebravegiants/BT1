# [?] fix: getTimeToNextGame crash when dispute game factory has zero or one games (#4492)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-04-14
Source: https://github.com/wevm/viem/commit/7b95669c23f86885bdd059f17d41f93c846b8dd6
Type: security-commit

## Details
fix: getTimeToNextGame crash when dispute game factory has zero or one games (#4492)

* fix: op-stack getTimeToNextGame for dispute games

* fix: single dispute games changes + tests

* chore: changeset

## Patch
### .changeset/fix-empty-dispute-games.md
```diff
@@ -0,0 +1,5 @@
+---
+"viem": patch
+---
+
+Fixed `getTimeToNextGame` crash when dispute game factory has zero or one games.
```

### src/op-stack/actions/getTimeToNextGame.test.ts
```diff
@@ -3,6 +3,7 @@ import { anvilMainnet } from '~test/anvil.js'
 import { reset } from '../../actions/index.js'
 import { optimism } from '../../op-stack/chains.js'
 import { getGames } from './getGames.js'
+import * as getGamesModule from './getGames.js'
 import { getTimeToNextGame } from './getTimeToNextGame.js'
 
 const client = anvilMainnet.getClient()
@@ -59,3 +60,34 @@ test('l2BlockNumber < latestGame.blockNumber', async () => {
   expect(seconds).toBe(0)
   expect(timestamp).toBe(undefined)
 })
+
+test('zero games (fresh chain)', async () => {                                                                                                           
+  const spy = vi.spyOn(getGamesModule, 'getGames').mockResolvedValueOnce([])
+  const result = await getTimeToNextGame(client, {                                                                                                       
+    l2BlockNumber: 1000n,
+    targetChain: optimism,
+  })                                                                                                                                                     
+  expect(result).toEqual({ interval: 0, seconds: 0, timestamp: undefined })
+  spy.mockRestore()                                                                                                                                      
+})              
+
+test('single game (no interval data)', async () => {
+  const spy = vi.spyOn(getGamesModule, 'getGames').mockResolvedValueOnce([
+    {                                                                                                                                                    
+      index: 0n,
+      metadata: '0x' as `0x${string}`,                                                                                                                   
+      timestamp: BigInt(Math.floor(Date.now() / 1000) - 3600),
+      rootClaim: '0x0000000000000000000000000000000000000000000000000000000000000000' as `0x${string}`,                                                  
+      extraData: '0x' as `0x${string}`,
+      l2BlockNumber: 500n,                                                                                                                               
+    },          
+  ])                                                                                                                                                     
+  const result = await getTimeToNextGame(client, {
+    l2BlockNumber: 1000n,
+    targetChain: optimism,                                                                                                                               
+  })
+  expect(result.interval).toBe(0)                                                                                                                        
+  expect(result.seconds).toBe(0)
+  expect(result.timestamp).toBeUndefined()
+  spy.mockRestore()
+})
\ No newline at end of file
```

### src/op-stack/actions/getTimeToNextGame.ts
```diff
@@ -87,6 +87,10 @@ export async function getTimeToNextGame<
     limit: 10,
   })
 
+  if (games.length === 0) {                                                                                                                              
+    return { interval: 0, seconds: 0, timestamp: undefined }                                                                                             
+  }           
+
   const deltas = games
     .map(({ l2BlockNumber, timestamp }, index) => {
       return index === games.length - 1
@@ -97,18 +101,17 @@ export async function getTimeToNextGame<
           ]
     })
     .filter(Boolean)
-  const interval = Math.ceil(
-    (deltas as [bigint, bigint][]).reduce(
-      (a, [b]) => Number(a) - Number(b),
-      0,
-    ) / deltas.length,
-  )
-  const blockInterval = Math.ceil(
-    (deltas as [bigint, bigint][]).reduce(
-      (a, [_, b]) => Number(a) - Number(b),
-      0,
-    ) / deltas.length,
-  )
+
+  const interval = deltas.length > 0                  
+    ? Math.ceil(                                                                                                                                         
+        (deltas as [bigint, bigint][]).reduce((a, [b]) => Number(a) - Number(b), 0) / deltas.length,
+      )                                                                                                                                                  
+    : 0                                               
+  const blockInterval = deltas.length > 0                                                                                                                
+    ? Math.ceil(                                 
+        (deltas as [bigint, bigint][]).reduce((a, [_, b]) => Number(a) - Number(b), 0) / deltas.length,
+      )                                                                                                                                                  
+    : 0
 
   const latestGame = games[0]
   const latestGameTimestamp = Number(latestGame.timestamp) * 1000
@@ -126,6 +129,9 @@ export async function getTimeToNextGame<
     // then we assume that the dispute game has already been submitted.
     if (latestGame.l2BlockNumber > l2BlockNumber) return 0
 
+    // If there is only a single game, no interval data
+    if (intervalWithBuffer === 0) return 0                                                                          
+
     const elapsedBlocks = Number(l2BlockNumber - latestGame.l2BlockNumber)
 
     const elapsed = Math.ceil((now - latestGameTimestamp) / 1000)
```
