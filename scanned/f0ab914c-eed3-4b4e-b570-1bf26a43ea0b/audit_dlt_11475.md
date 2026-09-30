# [?] quick fix for the inMsg deadlock

## Summary
Severity: Unknown
Chain: Cosmos
Component: informalsystems/hermes
Published: 2020-04-23
Source: https://github.com/informalsystems/hermes/commit/a0d7728426a90f22353b725f18aec0b71ffeb637
Type: security-commit

## Details
quick fix for the inMsg deadlock

## Patch
### verification/spec/connection-handshake/chm.tla
```diff
@@ -1,4 +1,4 @@
---------------------------------- MODULE CH ---------------------------------
+-------------------------------- MODULE CHM --------------------------------
 
 EXTENDS Naturals, FiniteSets
 
@@ -134,7 +134,7 @@ handleMsgConnectionOpenInit ==
  ***************************************************************************)
 
 \* Advance the height of the chain if MaxHeight is not yet reached.
-advanceChain ==
+advanceChainHeight ==
     /\ chModule.chainHeight < MaxHeight
     /\ chModule' = [chModule EXCEPT
                     !.chainHeight = chModule.chainHeight + 1
@@ -167,8 +167,9 @@ InitCHModule ==
     /\ outMsg = noMsg
 
 NextCHModule ==
-    \/ advanceChain
+    \/ advanceChainHeight
     \/ handleMsgConnectionOpenInit
+        /\ inMsg' = noMsg \* The chm consumed its inbound message. 
 
 (***************************************************************************
  Environment actions
@@ -211,10 +212,9 @@ Next ==
 /\ FlipTurn
 /\ IF turn = "chm" THEN
      /\ NextCHModule
-     /\ inMsg' = noMsg
    ELSE
      /\ NextEnv
-     /\ outMsg' = noMsg
+     /\ outMsg' = noMsg \* The env. consumed the outbound message.
      /\ UNCHANGED chModule
      \* Handle the exceptional case when turn is neither of chm or env?
 
@@ -234,7 +234,7 @@ THEOREM Spec => []TypeInvariant
 
 =============================================================================
 \* Modification History
-\* Last modified Wed Apr 22 17:43:57 CEST 2020 by adi
+\* Last modified Thu Apr 23 11:11:24 CEST 2020 by adi
 \* Wed Apr 22 10:42:14 CEST 2020 improvements & suggestions by anca & zarko
 \* Created Fri Apr 17 10:28:22 CEST 2020 by adi
 
```
