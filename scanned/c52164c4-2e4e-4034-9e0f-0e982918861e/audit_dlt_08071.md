# [?] accounts/abi: fix for one output interface crashing

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2017-12-29
Source: https://github.com/celo-org/celo-blockchain/commit/e7cd627d93d43ff52d13c66b336e12b96d9bfdef
Type: security-commit

## Details
accounts/abi: fix for one output interface crashing

## Patch
### accounts/abi/argument.go
```diff
@@ -169,6 +169,16 @@ func (arguments Arguments) unpackAtomic(v interface{}, output []byte) error {
 	if err != nil {
 		return err
 	}
+
+	// if we reach this part, there is only one output member from the contract event.
+	// for mobile, the result type is always a slice.
+	if reflect.Slice == value.Kind() && value.Len() >= 1 {
+		//check if it's not a byte slice
+		if reflect.TypeOf([]byte{}) != value.Type() {
+			value = value.Index(0).Elem()
+		}
+	}
+
 	return set(value, reflect.ValueOf(marshalledValue), arg)
 }
 
```
