# [?] consensus/clique: fix overflow on recent signer check around genesis

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-05-03
Source: https://github.com/scroll-tech/go-ethereum/commit/bcf2465b0b9c2aefcc7b79bdc24025f1497c08b1
Type: security-commit

## Details
consensus/clique: fix overflow on recent signer check around genesis

## Patch
### consensus/clique/clique.go
```diff
@@ -599,7 +599,7 @@ func (c *Clique) Seal(chain consensus.ChainReader, block *types.Block, stop <-ch
 	for seen, recent := range snap.Recents {
 		if recent == signer {
 			// Signer is among recents, only wait if the current block doens't shift it out
-			if limit := uint64(len(snap.Signers)/2 + 1); seen > number-limit {
+			if limit := uint64(len(snap.Signers)/2 + 1); number < limit || seen > number-limit {
 				log.Info("Signed recently, must wait for others")
 				<-stop
 				return nil, nil
```
