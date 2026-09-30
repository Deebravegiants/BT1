# [?] fixed second deadlock with inMsg

## Summary
Severity: Unknown
Chain: Cosmos
Component: informalsystems/hermes
Published: 2020-04-23
Source: https://github.com/informalsystems/hermes/commit/f590116d7c8f399f3ef21064e15dcb058be937d8
Type: security-commit

## Details
fixed second deadlock with inMsg

## Patch
### verification/spec/connection-handshake/chm.tla
```diff
@@ -125,9 +125,7 @@ handleMsgConnectionOpenInit ==
  /\ LET res == connectionOpenInit(chModule, inMsg) IN
       /\ chModule' = res.initCHM
       /\ outMsg' = res.msg
-      /\ UNCHANGED <<inMsg>>
-
-
+      /\ inMsg' = noMsg \* The chm consumed its inbound message.
 
 (***************************************************************************
  Connection Handshake Module actions.
@@ -137,8 +135,7 @@ handleMsgConnectionOpenInit ==
 advanceChainHeight ==
     /\ chModule.chainHeight < MaxHeight
     /\ chModule' = [chModule EXCEPT
-                    !.chainHeight = chModule.chainHeight + 1
-                 ]
+                        !.chainHeight = chModule.chainHeight + 1]
     /\ UNCHANGED <<outMsg, inMsg>>
 
 
@@ -168,8 +165,7 @@ InitCHModule ==
 
 NextCHModule ==
     \/ advanceChainHeight
-    \/ handleMsgConnectionOpenInit
-        /\ inMsg' = noMsg \* The chm consumed its inbound message. 
+    \/ handleMsgConnectionOpenInit 
 
 (***************************************************************************
  Environment actions
@@ -234,7 +230,7 @@ THEOREM Spec => []TypeInvariant
 
 =============================================================================
 \* Modification History
-\* Last modified Thu Apr 23 11:11:24 CEST 2020 by adi
+\* Last modified Thu Apr 23 11:22:41 CEST 2020 by adi
 \* Wed Apr 22 10:42:14 CEST 2020 improvements & suggestions by anca & zarko
 \* Created Fri Apr 17 10:28:22 CEST 2020 by adi
 
```
