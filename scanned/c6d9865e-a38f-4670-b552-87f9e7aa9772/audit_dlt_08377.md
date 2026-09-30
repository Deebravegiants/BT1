# [?] [Network] Avoid using unreachable!() to prevent DOS attacks.

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2020-08-28
Source: https://github.com/move-language/move/commit/089cb1c89da91c1125a64679e38e59e7482a6f4f
Type: security-commit

## Details
[Network] Avoid using unreachable!() to prevent DOS attacks.

Closes: #5807

## Patch
### network/src/interface/mod.rs
```diff
@@ -304,7 +304,10 @@ where
                 }
             }
             _ => {
-                unreachable!("Unexpected notification received from Peer actor");
+                warn!(
+                    "Unexpected notification received from Peer actor: {:?}",
+                    notif
+                );
             }
         }
     }
```

### network/src/peer_manager/mod.rs
```diff
@@ -762,9 +762,9 @@ where
                         );
                     }
                 } else {
-                    unreachable!(
-                        "{} Received network event for unregistered protocol",
-                        network_context
+                    debug!(
+                        "{} Received network message for unregistered protocol. Message: {:?}",
+                        network_context, msg,
                     );
                 }
             }
@@ -783,9 +783,9 @@ where
                         );
                     }
                 } else {
-                    unreachable!(
-                        "{} Received network event for unregistered protocol",
-                        network_context
+                    debug!(
+                        "{} Received network rpc request for unregistered protocol. RPC: {:?}",
+                        network_context, rpc_req,
                     );
                 }
             }
```

### network/src/protocols/direct_send/mod.rs
```diff
@@ -163,7 +163,7 @@ impl DirectSend {
                     error!("Unexpected message from peer actor: {:?}", message);
                 }
             }
-            _ => unreachable!("Unexpected PeerNotification"),
+            _ => warn!("Unexpected PeerNotification: {:?}", notif),
         }
     }
 
```
