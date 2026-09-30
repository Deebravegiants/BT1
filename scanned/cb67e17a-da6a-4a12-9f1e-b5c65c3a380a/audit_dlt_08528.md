# [?] Avoid crashing when the FE can’t connect to the web socket

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2021-03-05
Source: https://github.com/IntersectMBO/plutus/commit/57dd9e42ac0d975af719a388ab7e3f972a518e46
Type: security-commit

## Details
Avoid crashing when the FE can’t connect to the web socket

## Patch
### marlowe-dashboard-client/webpack.config.js
```diff
@@ -34,7 +34,10 @@ module.exports = {
             },
             "/ws": {
                 target: 'ws://localhost:8080',
-                ws: true
+                ws: true,
+                onError(err) {
+                  console.log('Error with the WebSocket:', err);
+                }
             }
         }
     },
```
