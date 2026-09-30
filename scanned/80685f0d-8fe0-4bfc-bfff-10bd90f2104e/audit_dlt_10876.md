# [?] Resolve "[Fix] Bifrost data race issue"

## Summary
Severity: Unknown
Chain: THORChain
Component: thorchain/thornode
Published: 2020-04-18
Source: https://github.com/thorchain/thornode/commit/343dbd70685db9d7819c7c0a91380fac0593b545
Type: security-commit

## Details
Resolve "[Fix] Bifrost data race issue"

## Patch
### cmd/bifrost/main.go
```diff
@@ -126,12 +126,10 @@ func main() {
 		log.Fatal().Err(err).Msg("fail to create tss instance")
 	}
 
-	go func() {
-		defer log.Info().Msg("tss instance exit")
-		if err := tssIns.Start(); err != nil {
-			log.Err(err).Msg("fail to start tss instance")
-		}
-	}()
+	if err := tssIns.Start(); err != nil {
+		log.Err(err).Msg("fail to start tss instance")
+	}
+
 	healthServer := NewHealthServer(cfg.TSS.InfoAddress, tssIns)
 	go func() {
 		defer log.Info().Msg("health server exit")
@@ -193,12 +191,10 @@ func main() {
 	if err := obs.Stop(); err != nil {
 		log.Fatal().Err(err).Msg("fail to stop observer")
 	}
-
 	// stop signer
 	if err := sign.Stop(); err != nil {
 		log.Fatal().Err(err).Msg("fail to stop signer")
 	}
-
 	// stop go tss
 	tssIns.Stop()
 	if err := healthServer.Stop(); err != nil {
```

### go.mod
```diff
@@ -42,7 +42,7 @@ require (
 	github.com/tendermint/tendermint v0.32.9
 	github.com/tendermint/tm-db v0.2.0
 	github.com/zondax/ledger-go v0.11.0 // indirect
-	gitlab.com/thorchain/tss/go-tss v0.0.0-20200415203509-b4003b73c39a
+	gitlab.com/thorchain/tss/go-tss v0.0.0-20200417204539-1af5be2c05a1
 	gitlab.com/thorchain/txscript v0.0.0-20200413023754-8aaf3443d92b
 	go.uber.org/multierr v1.5.0 // indirect
 	golang.org/x/crypto v0.0.0-20200414173820-0848c9571904 // indirect
```

### go.sum
```diff
@@ -885,6 +885,8 @@ github.com/zondax/ledger-go v0.11.0 h1:EEqUh6eaZucWAaGo87G7sJiqRNJpzBZr+I9PpGgjj
 github.com/zondax/ledger-go v0.11.0/go.mod h1:NI6JDs8VWwgh+9Bf1vPZMm9Xufp2Q7Iwm2IzxJWzmus=
 gitlab.com/thorchain/tss/go-tss v0.0.0-20200415203509-b4003b73c39a h1:ynXPVJOZVGcvfTCLjLSml+6QLxkY1jPBLUHdRwZwTQ0=
 gitlab.com/thorchain/tss/go-tss v0.0.0-20200415203509-b4003b73c39a/go.mod h1:NzfAS3WSwuhSJN3YXaeB/kg3wHOcaw986Fg+YU+ke5A=
+gitlab.com/thorchain/tss/go-tss v0.0.0-20200417204539-1af5be2c05a1 h1:hYlwLwNodezlg9KZf30tHTV7tzFlfrdR1QKU2ywQPJg=
+gitlab.com/thorchain/tss/go-tss v0.0.0-20200417204539-1af5be2c05a1/go.mod h1:NzfAS3WSwuhSJN3YXaeB/kg3wHOcaw986Fg+YU+ke5A=
 gitlab.com/thorchain/txscript v0.0.0-20200413023754-8aaf3443d92b h1:YHIcnYNNp7iCyQw6MXbiRSN0YtrpKR8E/fr7Y5HwDHM=
 gitlab.com/thorchain/txscript v0.0.0-20200413023754-8aaf3443d92b/go.mod h1:QwJJ+VjsoP0Cm9YC7ROmX0VIDuNxqBKIDGKRMkWkL3M=
 go.etcd.io/bbolt v1.3.2/go.mod h1:IbVyRI1SCnLcuJnV2u8VeU0CEYM7e686BmAb1XKL+uU=
```
