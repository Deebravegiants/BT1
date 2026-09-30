# [?] fix: DecodeRLP can panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-07-14
Source: https://github.com/filecoin-project/lotus/commit/871d1ba547b7cd35e70eddc2af90c195de0a3d26
Type: security-commit

## Details
fix: DecodeRLP can panic

## Patch
### chain/types/ethtypes/rlp.go
```diff
@@ -157,6 +157,9 @@ func decodeLength(data []byte, lenInBytes int) (length int, err error) {
 	if err := binary.Read(r, binary.BigEndian, &decodedLength); err != nil {
 		return 0, xerrors.Errorf("invalid rlp data: cannot parse string length: %w", err)
 	}
+	if decodedLength < 0 {
+		return 0, xerrors.Errorf("invalid rlp data: negative string length")
+	}
 	if lenInBytes+int(decodedLength) > len(data) {
 		return 0, xerrors.Errorf("invalid rlp data: out of bound while parsing list")
 	}
```

### chain/types/ethtypes/rlp_test.go
```diff
@@ -143,6 +143,19 @@ func TestDecodeList(t *testing.T) {
 	}
 }
 
+func TestDecodeNegativeLength(t *testing.T) {
+	testcases := [][]byte{
+		mustDecodeHex("0xbfffffffffffffff0041424344"),
+		mustDecodeHex("0xc1bFFF1111111111111111"),
+		mustDecodeHex("0xbFFF11111111111111"),
+	}
+
+	for _, tc := range testcases {
+		_, err := DecodeRLP(tc)
+		require.Error(t, err, "invalid rlp data: negative string length")
+	}
+}
+
 func TestDecodeEncodeTx(t *testing.T) {
 	testcases := [][]byte{
 		mustDecodeHex("0xdc82013a0185012a05f2008504a817c8008080872386f26fc1000000c0"),
```
