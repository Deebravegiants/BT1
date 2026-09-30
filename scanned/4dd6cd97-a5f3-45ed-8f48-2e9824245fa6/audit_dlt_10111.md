# [?] Fix crash on consensus watch-only nodes (#645)

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2019-03-21
Source: https://github.com/neo-project/neo/commit/7e82bcad2d95c223bc255710bd7676e85d26168b
Type: security-commit

## Details
Fix crash on consensus watch-only nodes (#645)

* Fix crash on consensus watch-only nodes

This commit fix the relay of payloads and ensures this interesting feature.

## Patch
### neo/Consensus/ConsensusService.cs
```diff
@@ -72,7 +72,7 @@ private bool AddTransaction(Transaction tx, bool verify)
                 {
                     // if we are the primary for this view, but acting as a backup because we recovered our own
                     // previously sent prepare request, then we don't want to send a prepare response.
-                    if (context.MyIndex == context.PrimaryIndex) return true;
+                    if (context.IsPrimary() || context.WatchOnly()) return true;
 
                     Log($"send prepare response");
                     localNode.Tell(new LocalNode.SendDirectly { Inventory = context.MakePrepareResponse() });
@@ -112,9 +112,12 @@ private void CheckExpectedView(byte viewNumber)
             if (context.ViewNumber == viewNumber) return;
             if (context.ChangeViewPayloads.Count(p => p != null && p.GetDeserializedMessage<ChangeView>().NewViewNumber == viewNumber) >= context.M())
             {
-                ChangeView message = context.ChangeViewPayloads[context.MyIndex]?.GetDeserializedMessage<ChangeView>();
-                if (message is null || message.NewViewNumber < viewNumber)
-                    localNode.Tell(new LocalNode.SendDirectly { Inventory = context.MakeChangeView(viewNumber) });
+                if (!context.WatchOnly())
+                {
+                    ChangeView message = context.ChangeViewPayloads[context.MyIndex]?.GetDeserializedMessage<ChangeView>();
+                    if (message is null || message.NewViewNumber < viewNumber)
+                        localNode.Tell(new LocalNode.SendDirectly { Inventory = context.MakeChangeView(viewNumber) });
+                }
                 InitializeConsensus(viewNumber);
             }
         }
@@ -145,10 +148,10 @@ private byte GetLastExpectedView(int validatorIndex)
         private void InitializeConsensus(byte viewNumber)
         {
             context.Reset(viewNumber);
-            if (context.MyIndex < 0) return;
             if (viewNumber > 0)
                 Log($"changeview: view={viewNumber} primary={context.Validators[context.GetPrimaryIndex((byte)(viewNumber - 1u))]}", LogLevel.Warning);
-            Log($"initialize: height={context.BlockIndex} view={viewNumber} index={context.MyIndex} role={(context.IsPrimary() ? "Primary" : "Backup")}");
+            Log($"initialize: height={context.BlockIndex} view={viewNumber} index={context.MyIndex} role={(context.IsPrimary() ? "Primary" : context.WatchOnly() ? "WatchOnly" : "Backup")}");
+            if (context.WatchOnly()) return;
             if (context.IsPrimary())
             {
                 if (isRecovering)
@@ -186,6 +189,7 @@ private void OnChangeViewReceived(ConsensusPayload payload, ChangeView message)
             if (!knownHashes.Add(payload.Hash)) return;
             if (message.NewViewNumber <= context.ViewNumber)
             {
+                if (context.WatchOnly()) return;
                 bool shouldSendRecovery = false;
                 // Limit recovery to sending from `f` nodes when the request is from a lower view number.
                 int allowedRecoveryNodeCount = context.F();
@@ -365,7 +369,6 @@ private void OnPrepareRequestReceived(ConsensusPayload payload, PrepareRequest m
                     if (!Crypto.Default.VerifySignature(hashData, context.CommitPayloads[i].GetDeserializedMessage<Commit>().Signature, context.Validators[i].EncodePoint(false)))
                         context.CommitPayloads[i] = null;
             Dictionary<UInt256, Transaction> mempoolVerified = Blockchain.Singleton.MemPool.GetVerifiedTransactions().ToDictionary(p => p.Hash);
-
             List<Transaction> unverified = new List<Transaction>();
             foreach (UInt256 hash in context.TransactionHashes.Skip(1))
             {
@@ -401,7 +404,7 @@ private void OnPrepareResponseReceived(ConsensusPayload payload, PrepareResponse
                 return;
             Log($"{nameof(OnPrepareResponseReceived)}: height={payload.BlockIndex} view={message.ViewNumber} index={payload.ValidatorIndex}");
             context.PreparationPayloads[payload.ValidatorIndex] = payload;
-            if (context.CommitSent()) return;
+            if (context.WatchOnly() || context.CommitSent()) return;
             if (context.RequestSentOrReceived())
                 CheckPreparations();
         }
@@ -458,13 +461,13 @@ private void OnStart(Start options)
             }
             InitializeConsensus(0);
             // Issue a ChangeView with NewViewNumber of 0 to request recovery messages on start-up.
-            if (context.BlockIndex == Blockchain.Singleton.HeaderHeight + 1)
+            if (context.BlockIndex == Blockchain.Singleton.HeaderHeight + 1 && !context.WatchOnly())
                 localNode.Tell(new LocalNode.SendDirectly { Inventory = context.MakeChangeView(0) });
         }
 
         private void OnTimer(Timer timer)
         {
-            if (context.BlockSent()) return;
+            if (context.WatchOnly() || context.BlockSent()) return;
             if (timer.Height != context.BlockIndex || timer.ViewNumber != context.ViewNumber) return;
             Log($"timeout: height={timer.Height} view={timer.ViewNumber}");
             if (context.IsPrimary() && !context.RequestSentOrReceived())
@@ -517,6 +520,7 @@ public static Props Props(IActorRef localNode, IActorRef taskManager, Store stor
 
         private void RequestChangeView()
         {
+            if (context.WatchOnly()) return;
             byte expectedView = context.ChangeViewPayloads[context.MyIndex]?.GetDeserializedMessage<ChangeView>().NewViewNumber ?? 0;
             if (expectedView < context.ViewNumber) expectedView = context.ViewNumber;
             expectedView++;
```

### neo/Consensus/Helper.cs
```diff
@@ -1,4 +1,4 @@
-﻿using Neo.Network.P2P.Payloads;
+using Neo.Network.P2P.Payloads;
 using Neo.Persistence;
 using System.Runtime.CompilerServices;
 
@@ -15,19 +15,21 @@ internal static class Helper
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
         public static bool IsBackup(this IConsensusContext context) => context.MyIndex >= 0 && context.MyIndex != context.PrimaryIndex;
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
+        public static bool WatchOnly(this IConsensusContext context) => context.MyIndex < 0;
+        [MethodImpl(MethodImplOptions.AggressiveInlining)]
         public static Header PrevHeader(this IConsensusContext context) => context.Snapshot.GetHeader(context.PrevHash);
 
         // Consensus States
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
         public static bool RequestSentOrReceived(this IConsensusContext context) => context.PreparationPayloads[context.PrimaryIndex] != null;
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
-        public static bool ResponseSent(this IConsensusContext context) => context.PreparationPayloads[context.MyIndex] != null;
+        public static bool ResponseSent(this IConsensusContext context) => !context.WatchOnly() && context.PreparationPayloads[context.MyIndex] != null;
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
-        public static bool CommitSent(this IConsensusContext context) => context.CommitPayloads[context.MyIndex] != null;
+        public static bool CommitSent(this IConsensusContext context) => !context.WatchOnly() && context.CommitPayloads[context.MyIndex] != null;
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
         public static bool BlockSent(this IConsensusContext context) => context.Block != null;
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
-        public static bool ViewChanging(this IConsensusContext context) => context.ChangeViewPayloads[context.MyIndex]?.GetDeserializedMessage<ChangeView>().NewViewNumber > context.ViewNumber;
+        public static bool ViewChanging(this IConsensusContext context) => !context.WatchOnly() && context.ChangeViewPayloads[context.MyIndex]?.GetDeserializedMessage<ChangeView>().NewViewNumber > context.ViewNumber;
 
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
         public static uint GetPrimaryIndex(this IConsensusContext context, byte viewNumber)
```
