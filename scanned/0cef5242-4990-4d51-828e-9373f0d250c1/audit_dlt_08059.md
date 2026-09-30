# [?] abi, signer: fix nil dereference in #17633 (#17653) 

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-09-19
Source: https://github.com/celo-org/celo-blockchain/commit/16bc8741bfc6db6d7d352015e4324042dd9288a4
Type: security-commit

## Details
abi, signer: fix nil dereference in #17633 (#17653) 

* abi,signer: fix nil dereference in #17633

* signer/core: tiny typo fix in test error message

## Patch
### accounts/abi/type.go
```diff
@@ -103,7 +103,12 @@ func NewType(t string) (typ Type, err error) {
 		return typ, err
 	}
 	// parse the type and size of the abi-type.
-	parsedType := typeRegex.FindAllStringSubmatch(t, -1)[0]
+	matches := typeRegex.FindAllStringSubmatch(t, -1)
+	if len(matches) == 0 {
+		return Type{}, fmt.Errorf("invalid type '%v'", t)
+	}
+	parsedType := matches[0]
+
 	// varSize is the size of the variable
 	var varSize int
 	if len(parsedType[3]) > 0 {
```

### signer/core/abihelper_test.go
```diff
@@ -100,16 +100,6 @@ func TestNewUnpacker(t *testing.T) {
 
 }
 
-/*
-func TestReflect(t *testing.T) {
-	a := big.NewInt(0)
-	b := new(big.Int).SetBytes([]byte{0x00})
-	if !reflect.DeepEqual(a, b) {
-		t.Fatalf("Nope, %v != %v", a, b)
-	}
-}
-*/
-
 func TestCalldataDecoding(t *testing.T) {
 
 	// send(uint256)                              : a52c101e
@@ -123,7 +113,7 @@ func TestCalldataDecoding(t *testing.T) {
 	{"type":"function","name":"sam","inputs":[{"name":"a","type":"bytes"},{"name":"a","type":"bool"},{"name":"a","type":"uint256[]"}]}
 ]`
 	//Expected failures
-	for _, hexdata := range []string{
+	for i, hexdata := range []string{
 		"a52c101e00000000000000000000000000000000000000000000000000000000000000120000000000000000000000000000000000000000000000000000000000000042",
 		"a52c101e000000000000000000000000000000000000000000000000000000000000001200",
 		"a52c101e00000000000000000000000000000000000000000000000000000000000000",
@@ -145,12 +135,11 @@ func TestCalldataDecoding(t *testing.T) {
 	} {
 		_, err := parseCallData(common.Hex2Bytes(hexdata), jsondata)
 		if err == nil {
-			t.Errorf("Expected decoding to fail: %s", hexdata)
+			t.Errorf("test %d: expected decoding to fail: %s", i, hexdata)
 		}
 	}
-
 	//Expected success
-	for _, hexdata := range []string{
+	for i, hexdata := range []string{
 		// From https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI
 		"a5643bf20000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000464617665000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003",
 		"a52c101e0000000000000000000000000000000000000000000000000000000000000012",
@@ -169,7 +158,7 @@ func TestCalldataDecoding(t *testing.T) {
 	} {
 		_, err := parseCallData(common.Hex2Bytes(hexdata), jsondata)
 		if err != nil {
-			t.Errorf("Unexpected failure on input %s:\n %v (%d bytes) ", hexdata, err, len(common.Hex2Bytes(hexdata)))
+			t.Errorf("test %d: unexpected failure on input %s:\n %v (%d bytes) ", i, hexdata, err, len(common.Hex2Bytes(hexdata)))
 		}
 	}
 }
@@ -245,3 +234,18 @@ func TestCustomABI(t *testing.T) {
 		t.Fatalf("Save failed: should find a match for abi signature after loading from disk")
 	}
 }
+
+func TestMaliciousAbiStrings(t *testing.T) {
+	tests := []string{
+		"func(uint256,uint256,[]uint256)",
+		"func(uint256,uint256,uint256,)",
+		"func(,uint256,uint256,uint256)",
+	}
+	data := common.Hex2Bytes("4401a6e40000000000000000000000000000000000000000000000000000000000000012")
+	for i, tt := range tests {
+		_, err := testSelector(tt, data)
+		if err == nil {
+			t.Errorf("test %d: expected error for selector '%v'", i, tt)
+		}
+	}
+}
```
