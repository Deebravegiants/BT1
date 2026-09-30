# [?] core/node: fix divide by zero fatal crash for reprovide rate check (#10411)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2024-05-06
Source: https://github.com/ipfs/kubo/commit/65ff6196290dca25c724048b8c1f1e5bbe260442
Type: security-commit

## Details
core/node: fix divide by zero fatal crash for reprovide rate check (#10411)

## Patch
### core/node/provider.go
```diff
@@ -83,7 +83,11 @@ https://github.com/ipfs/kubo/blob/master/docs/config.md#routingaccelerateddhtcli
 					}
 
 					// How long per block that lasts us.
-					expectedProvideSpeed := reprovideInterval / time.Duration(count)
+					expectedProvideSpeed := reprovideInterval
+					if count > 0 {
+						expectedProvideSpeed = reprovideInterval / time.Duration(count)
+					}
+
 					if avgProvideSpeed > expectedProvideSpeed {
 						logger.Errorf(`
 🔔🔔🔔 YOU ARE FALLING BEHIND DHT REPROVIDES! 🔔🔔🔔
```
