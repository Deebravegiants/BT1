# [?] Fix two potential arithmetic underflow errors (#484)

## Summary
Severity: Unknown
Chain: Kadena
Component: kadena-io/chainweb-node
Published: 2019-09-29
Source: https://github.com/kadena-io/chainweb-node/commit/963d882900941e0265082884b8946ace93a90154
Type: security-commit

## Details
Fix two potential arithmetic underflow errors (#484)

## Patch
### src/P2P/Node.hs
```diff
@@ -397,7 +397,7 @@ findNextPeer conf node = do
             $ s
 
         shiftR s = do
-            i <- randomR node (0, size s - 1)
+            i <- randomR node (0, max 1 (size s) - 1)
             return $! shift i s
 
     -- Classify the peers by priority
```

### src/P2P/Node/PeerDB.hs
```diff
@@ -354,7 +354,7 @@ incrementActiveSessionCount db i
 
 decrementActiveSessionCount :: PeerDb -> PeerInfo -> IO ()
 decrementActiveSessionCount db i
-    = updatePeerDb db (_peerAddr i) $ over peerEntryActiveSessionCount pred
+    = updatePeerDb db (_peerAddr i) $ over peerEntryActiveSessionCount (pred . max 1)
 
 incrementSuccessiveFailures :: PeerDb -> PeerInfo -> IO ()
 incrementSuccessiveFailures db i
```
