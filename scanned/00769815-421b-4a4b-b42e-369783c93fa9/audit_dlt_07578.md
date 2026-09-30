# [?] eth/gasestimator: fix potential overflow (#32255)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-07-23
Source: https://github.com/ethereum/go-ethereum/commit/3b67602c4c5e701028c7246977aabff02cce643c
Type: security-commit

## Details
eth/gasestimator: fix potential overflow (#32255)

Improve binary search, preventing the potential overflow in certain L2 cases

## Patch
### eth/gasestimator/gasestimator.go
```diff
@@ -170,7 +170,7 @@ func Estimate(ctx context.Context, call *core.Message, opts *Options, gasCap uin
 				break
 			}
 		}
-		mid := (hi + lo) / 2
+		mid := lo + (hi-lo)/2
 		if mid > lo*2 {
 			// Most txs don't need much higher gas limit than their gas used, and most txs don't
 			// require near the full block limit of gas, so the selection of where to bisect the
```
