# [?] consensus/misc/eip4844: small update to fix simulatev1 crash (#2054)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2026-02-13
Source: https://github.com/0xPolygon/bor/commit/a2a67b720d7e3ce5ce859a9e129445a8a88af069
Type: security-commit

## Details
consensus/misc/eip4844: small update to fix simulatev1 crash (#2054)

## Patch
### consensus/misc/eip4844/eip4844.go
```diff
@@ -123,6 +123,9 @@ func VerifyEIP4844Header(config *params.ChainConfig, parent, header *types.Heade
 func CalcExcessBlobGas(config *params.ChainConfig, parent *types.Header, headTimestamp uint64) uint64 {
 	isOsaka := config.IsOsaka(config.LondonBlock)
 	bcfg := latestBlobConfig(config, headTimestamp)
+	if bcfg == nil {
+		return 0
+	}
 	return calcExcessBlobGas(isOsaka, bcfg, parent)
 }
 
```
