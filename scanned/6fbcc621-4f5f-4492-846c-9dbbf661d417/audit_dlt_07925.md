# [?] fix: check integer overflow when decode crosschain payload (#1679)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2023-06-08
Source: https://github.com/bnb-chain/bsc/commit/78ad0496419338d4c77bac04f76feda04e247a81
Type: security-commit

## Details
fix: check integer overflow when decode crosschain payload (#1679)

## Patch
### core/vm/lightclient/v2/lightclient.go
```diff
@@ -194,6 +194,11 @@ func DecodeLightBlockValidationInput(input []byte) (*ConsensusState, *types.Ligh
 	}
 
 	csLen := binary.BigEndian.Uint64(input[consensusStateLengthBytesLength-uint64TypeLength : consensusStateLengthBytesLength])
+
+	if consensusStateLengthBytesLength+csLen < consensusStateLengthBytesLength {
+		return nil, nil, fmt.Errorf("integer overflow, csLen: %d", csLen)
+	}
+
 	if uint64(len(input)) <= consensusStateLengthBytesLength+csLen {
 		return nil, nil, fmt.Errorf("expected payload size %d, actual size: %d", consensusStateLengthBytesLength+csLen, len(input))
 	}
```
