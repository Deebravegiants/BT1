# [?] Fix panic in conn open try when no connection id is provided (#615)

## Summary
Severity: Unknown
Chain: Cosmos
Component: informalsystems/ibc-rs
Published: 2021-02-09
Source: https://github.com/informalsystems/ibc-rs/commit/f291150e86175ef60118ef8882249b1a8cfacbd3
Type: security-commit

## Details
Fix panic in conn open try when no connection id is provided (#615)

## Patch
### modules/src/ics03_connection/context.rs
```diff
@@ -72,14 +72,14 @@ pub trait ConnectionKeeper {
                 )?;
             }
             State::TryOpen => {
-                self.store_connection(
-                    &result.connection_id.clone().unwrap(),
-                    &result.connection_end,
-                )?;
+                let connection_id = result
+                    .connection_id
+                    .unwrap_or_else(|| self.next_connection_id());
+                self.store_connection(&connection_id, &result.connection_end)?;
                 // If this is the first time the handler processed this connection, associate the
                 // connection end to its client identifier.
                 self.store_connection_to_client(
-                    &result.connection_id.clone().unwrap(),
+                    &connection_id,
                     &result.connection_end.client_id(),
                 )?;
             }
```
