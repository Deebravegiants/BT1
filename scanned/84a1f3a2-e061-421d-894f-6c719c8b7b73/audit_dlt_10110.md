# [?] Fix crash in consensus (#698)

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2019-04-10
Source: https://github.com/neo-project/neo/commit/3a06f9c0efcc3cc267d380bb945fe7474b1f2243
Type: security-commit

## Details
Fix crash in consensus (#698)

## Patch
### neo/Consensus/ConsensusService.cs
```diff
@@ -11,6 +11,7 @@
 using Neo.Wallets;
 using System;
 using System.Collections.Generic;
+using System.IO;
 using System.Linq;
 
 namespace Neo.Consensus
@@ -261,11 +262,24 @@ private void OnConsensusPayload(ConsensusPayload payload)
                 return;
             }
             if (payload.ValidatorIndex >= context.Validators.Length) return;
+            ConsensusMessage message;
+            try
+            {
+                message = payload.ConsensusMessage;
+            }
+            catch (FormatException)
+            {
+                return;
+            }
+            catch (IOException)
+            {
+                return;
+            }
             context.LastSeenMessage[payload.ValidatorIndex] = (int) payload.BlockIndex;
             foreach (IP2PPlugin plugin in Plugin.P2PPlugins)
                 if (!plugin.OnConsensusMessage(payload))
                     return;
-            switch (payload.ConsensusMessage)
+            switch (message)
             {
                 case ChangeView view:
                     OnChangeViewReceived(payload, view);
```
