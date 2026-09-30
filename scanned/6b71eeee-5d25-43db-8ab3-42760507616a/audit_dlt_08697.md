# [?] Avoid nil pointer dereference

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-17
Source: https://github.com/OffchainLabs/nitro/commit/ebd310ef56e17d647927e9c15baadd50327dc06d
Type: security-commit

## Details
Avoid nil pointer dereference

## Patch
### arbos/tx_processor.go
```diff
@@ -874,9 +874,9 @@ func (p *TxProcessor) DropTip() bool {
 		return true
 	}
 	// v60+: collect tips if the tip meets or exceeds the floor
-	floor, _ := p.state.TipCapFloor()
-	if floor.Sign() == 0 {
-		return true // floor set to 0: drop all tips
+	floor, err := p.state.TipCapFloor()
+	if err != nil || floor.Sign() == 0 {
+		return true // safe default: drop tips
 	}
 
 	// proposed tip is the difference between the gas price and the base fee
```
