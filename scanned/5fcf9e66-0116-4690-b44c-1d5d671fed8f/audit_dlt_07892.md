# [?] core/vm: cap CometBFT light client validator count to prevent DoS (#3575)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2026-02-25
Source: https://github.com/bnb-chain/bsc/commit/037a309e92eeec23bbafb0a7771bd41728ba79b3
Type: security-commit

## Details
core/vm: cap CometBFT light client validator count to prevent DoS (#3575)

## Patch
### core/vm/lightclient/v2/lightclient.go
```diff
@@ -143,6 +143,9 @@ func DecodeConsensusState(input []byte) (ConsensusState, error) {
 	if inputLen <= minimumLength || (inputLen-minimumLength)%singleValidatorBytesLength != 0 {
 		return ConsensusState{}, fmt.Errorf("expected input size %d+%d*N, actual input size: %d", minimumLength, singleValidatorBytesLength, inputLen)
 	}
+	if inputLen > maxConsensusStateLength {
+		return ConsensusState{}, fmt.Errorf("consensus state too large: %d bytes exceeds maximum %d (max 99 validators)", inputLen, maxConsensusStateLength)
+	}
 
 	pos := uint64(0)
 	chainID := string(bytes.Trim(input[pos:pos+chainIDLength], "\x00"))
```
