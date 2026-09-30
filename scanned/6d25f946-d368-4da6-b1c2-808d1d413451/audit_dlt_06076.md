# [?] accounts/abi: validate fieldnames to avoid reflect.StructOf panic (#24932) (#678)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin
Published: 2025-02-13
Source: https://github.com/axieinfinity/ronin-archive/commit/6ec7d951ad4c33f1212abdda6452f0f3b3d05adf
Type: security-commit

## Details
accounts/abi: validate fieldnames to avoid reflect.StructOf panic (#24932) (#678)

commit https://github.com/ethereum/go-ethereum/commit/af02e97929d47238fa0dbd233846270802b99e1a.

Reported-by: eugenioclrc <eugenioclrc@gmail.com>
Co-authored-by: Martin Holst Swende <martin@swende.se>

## Patch
### accounts/abi/bind/base_test.go
```diff
@@ -341,3 +341,11 @@ func newMockLog(topics []common.Hash, txHash common.Hash) types.Log {
 		Removed:     false,
 	}
 }
+
+// TestCrashers contains some strings which previously caused the abi codec to crash.
+func TestCrashers(t *testing.T) {
+	abi.JSON(strings.NewReader(`[{"inputs":[{"type":"tuple[]","components":[{"type":"bool","name":"_1"}]}]}]`))
+	abi.JSON(strings.NewReader(`[{"inputs":[{"type":"tuple[]","components":[{"type":"bool","name":"&"}]}]}]`))
+	abi.JSON(strings.NewReader(`[{"inputs":[{"type":"tuple[]","components":[{"type":"bool","name":"----"}]}]}]`))
+	abi.JSON(strings.NewReader(`[{"inputs":[{"type":"tuple[]","components":[{"type":"bool","name":"foo.Bar"}]}]}]`))
+}
```

### accounts/abi/type.go
```diff
@@ -23,6 +23,8 @@ import (
 	"regexp"
 	"strconv"
 	"strings"
+	"unicode"
+	"unicode/utf8"
 
 	"github.com/ethereum/go-ethereum/common"
 )
@@ -173,6 +175,9 @@ func NewType(t string, internalType string, components []ArgumentMarshaling) (ty
 			if err != nil {
 				return Type{}, err
 			}
+			if !isValidFieldName(fieldName) {
+				return Type{}, fmt.Errorf("field %d has invalid name", idx)
+			}
 			overloadedNames[fieldName] = fieldName
 			fields = append(fields, reflect.StructField{
 				Name: fieldName, // reflect.StructOf will panic for any exported field.
@@ -399,3 +404,30 @@ func getTypeSize(t Type) int {
 	}
 	return 32
 }
+
+// isLetter reports whether a given 'rune' is classified as a Letter.
+// This method is copied from reflect/type.go
+func isLetter(ch rune) bool {
+	return 'a' <= ch && ch <= 'z' || 'A' <= ch && ch <= 'Z' || ch == '_' || ch >= utf8.RuneSelf && unicode.IsLetter(ch)
+}
+
+// isValidFieldName checks if a string is a valid (struct) field name or not.
+//
+// According to the language spec, a field name should be an identifier.
+//
+// identifier = letter { letter | unicode_digit } .
+// letter = unicode_letter | "_" .
+// This method is copied from reflect/type.go
+func isValidFieldName(fieldName string) bool {
+	for i, c := range fieldName {
+		if i == 0 && !isLetter(c) {
+			return false
+		}
+
+		if !(isLetter(c) || unicode.IsDigit(c)) {
+			return false
+		}
+	}
+
+	return len(fieldName) > 0
+}
```
