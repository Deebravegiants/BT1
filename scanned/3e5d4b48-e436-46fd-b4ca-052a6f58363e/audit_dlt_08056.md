# [?] accounts/abi: fix panic in MethodById lookup. Fixes #17797 (#17798)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-10-01
Source: https://github.com/celo-org/celo-blockchain/commit/96fd50be10885c9b3033404df698177fdb63d036
Type: security-commit

## Details
accounts/abi: fix panic in MethodById lookup. Fixes #17797 (#17798)

## Patch
### accounts/abi/abi.go
```diff
@@ -137,6 +137,9 @@ func (abi *ABI) UnmarshalJSON(data []byte) error {
 // MethodById looks up a method by the 4-byte id
 // returns nil if none found
 func (abi *ABI) MethodById(sigdata []byte) (*Method, error) {
+	if len(sigdata) < 4 {
+		return nil, fmt.Errorf("data too short (% bytes) for abi method lookup", len(sigdata))
+	}
 	for _, method := range abi.Methods {
 		if bytes.Equal(method.Id(), sigdata[:4]) {
 			return &method, nil
```

### accounts/abi/abi_test.go
```diff
@@ -711,5 +711,14 @@ func TestABI_MethodById(t *testing.T) {
 			t.Errorf("Method %v (id %v) not 'findable' by id in ABI", name, common.ToHex(m.Id()))
 		}
 	}
-
+	// Also test empty
+	if _, err := abi.MethodById([]byte{0x00}); err == nil {
+		t.Errorf("Expected error, too short to decode data")
+	}
+	if _, err := abi.MethodById([]byte{}); err == nil {
+		t.Errorf("Expected error, too short to decode data")
+	}
+	if _, err := abi.MethodById(nil); err == nil {
+		t.Errorf("Expected error, nil is short to decode data")
+	}
 }
```
