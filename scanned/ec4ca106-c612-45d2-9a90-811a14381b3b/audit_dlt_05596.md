# [?] triedb/pathdb: fix index out of range panic in decodeSingle (#32937)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-10-20
Source: https://github.com/ethereum/go-ethereum/commit/11c0fb98af8ba14deb6abe77b357cbe927ba05ba
Type: security-commit

## Details
triedb/pathdb: fix index out of range panic in decodeSingle (#32937)

Fixes TestCorruptedKeySection flaky test failure.
https://github.com/ethereum/go-ethereum/actions/runs/18600235182/job/53037084761?pr=32920

## Patch
### triedb/pathdb/history_trienode.go
```diff
@@ -370,11 +370,15 @@ func decodeSingle(keySection []byte, onValue func([]byte, int, int) error) ([]st
 	for keyOff < keyLimit {
 		// Validate the key and value offsets within the single trie data chunk
 		if items%trienodeDataBlockRestartLen == 0 {
-			if keyOff != int(keyOffsets[items/trienodeDataBlockRestartLen]) {
-				return nil, fmt.Errorf("key offset is not matched, recorded: %d, want: %d", keyOffsets[items/trienodeDataBlockRestartLen], keyOff)
+			restartIndex := items / trienodeDataBlockRestartLen
+			if restartIndex >= len(keyOffsets) {
+				return nil, fmt.Errorf("restart index out of range: %d, available restarts: %d", restartIndex, len(keyOffsets))
 			}
-			if valOff != int(valOffsets[items/trienodeDataBlockRestartLen]) {
-				return nil, fmt.Errorf("value offset is not matched, recorded: %d, want: %d", valOffsets[items/trienodeDataBlockRestartLen], valOff)
+			if keyOff != int(keyOffsets[restartIndex]) {
+				return nil, fmt.Errorf("key offset is not matched, recorded: %d, want: %d", keyOffsets[restartIndex], keyOff)
+			}
+			if valOff != int(valOffsets[restartIndex]) {
+				return nil, fmt.Errorf("value offset is not matched, recorded: %d, want: %d", valOffsets[restartIndex], valOff)
 			}
 		}
 		// Resolve the entry from key section
```
