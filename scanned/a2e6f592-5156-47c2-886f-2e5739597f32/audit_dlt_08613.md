# [?] fix: ethtypes: handle length overflow case

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-07-17
Source: https://github.com/filecoin-project/lotus/commit/990b5a0bade9c22a93b95af265027f2fa351c271
Type: security-commit

## Details
fix: ethtypes: handle length overflow case

## Patch
### chain/types/ethtypes/rlp.go
```diff
@@ -134,7 +134,7 @@ func decodeRLP(data []byte) (res interface{}, consumed int, err error) {
 			return nil, 0, err
 		}
 		totalLen := 1 + strLenInBytes + strLen
-		if totalLen > len(data) {
+		if totalLen > len(data) || totalLen < 0 {
 			return nil, 0, xerrors.Errorf("invalid rlp data: out of bound while parsing string")
 		}
 		return data[1+strLenInBytes : totalLen], totalLen, nil
@@ -160,7 +160,9 @@ func decodeLength(data []byte, lenInBytes int) (length int, err error) {
 	if decodedLength < 0 {
 		return 0, xerrors.Errorf("invalid rlp data: negative string length")
 	}
-	if lenInBytes+int(decodedLength) > len(data) {
+
+	totalLength := lenInBytes + int(decodedLength)
+	if totalLength < 0 || totalLength > len(data) {
 		return 0, xerrors.Errorf("invalid rlp data: out of bound while parsing list")
 	}
 	return int(decodedLength), nil
```

### chain/types/ethtypes/rlp_test.go
```diff
@@ -148,11 +148,12 @@ func TestDecodeNegativeLength(t *testing.T) {
 		mustDecodeHex("0xbfffffffffffffff0041424344"),
 		mustDecodeHex("0xc1bFFF1111111111111111"),
 		mustDecodeHex("0xbFFF11111111111111"),
+		mustDecodeHex("0xbf7fffffffffffffff41424344"),
 	}
 
 	for _, tc := range testcases {
 		_, err := DecodeRLP(tc)
-		require.Error(t, err, "invalid rlp data: negative string length")
+		require.ErrorContains(t, err, "invalid rlp data")
 	}
 }
 
```
