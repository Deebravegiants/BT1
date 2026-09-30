# [?] fix nil pointer crash

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-05-24
Source: https://github.com/harmony-one/harmony/commit/72281aff09c6bd27722b2010d7b5d9d39a66b003
Type: security-commit

## Details
fix nil pointer crash

Signed-off-by: Leo Chen <leo@harmony.one>

## Patch
### internal/chain/engine.go
```diff
@@ -172,6 +172,9 @@ func (e *engineImpl) VerifySeal(chain engine.ChainReader, header *block.Header)
 	if chain.CurrentHeader().Number().Uint64() <= uint64(1) {
 		return nil
 	}
+	if header == nil {
+		return errors.New("[VerifySeal] nil block header")
+	}
 	publicKeys, err := ReadPublicKeysFromLastBlock(chain, header)
 
 	if err != nil {
```
