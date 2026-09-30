# [?] Fix #3965 (potential crashes when routing certain gossip messages) (#3978)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-08-17
Source: https://github.com/status-im/nimbus-eth2/commit/fa9e2b4ec41850c45db4787d46e1590387f46240
Type: security-commit

## Details
Fix #3965 (potential crashes when routing certain gossip messages) (#3978)

## Patch
### beacon_chain/validators/message_router.nim
```diff
@@ -429,7 +429,7 @@ proc routeSignedVoluntaryExit*(
     if not res.isGoodForSending:
       warn "Voluntary exit failed validation",
         exit = shortLog(exit), error = res.error()
-    return err(res.error()[1])
+      return err(res.error()[1])
 
   let res = await router[].network.broadcastVoluntaryExit(exit)
   if res.isOk():
@@ -449,7 +449,7 @@ proc routeAttesterSlashing*(
     if not res.isGoodForSending:
       warn "Attester slashing failed validation",
         slashing = shortLog(slashing), error = res.error()
-    return err(res.error()[1])
+      return err(res.error()[1])
 
   let res = await router[].network.broadcastAttesterSlashing(slashing)
   if res.isOk():
@@ -470,7 +470,7 @@ proc routeProposerSlashing*(
     if not res.isGoodForSending:
       warn "Proposer slashing request failed validation",
         slashing = shortLog(slashing), error = res.error()
-    return err(res.error()[1])
+      return err(res.error()[1])
 
   let res = await router[].network.broadcastProposerSlashing(slashing)
   if res.isOk():
```
