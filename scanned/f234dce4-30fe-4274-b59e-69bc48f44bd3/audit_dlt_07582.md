# [?] common/math: fix out of bounds access in json unmarshalling (#30014)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-06-17
Source: https://github.com/ethereum/go-ethereum/commit/d8664490da47bfff1854869826268c486e6487d7
Type: security-commit

## Details
common/math: fix out of bounds access in json unmarshalling (#30014)


Co-authored-by: Martin Holst Swende <martin@swende.se>

## Patch
### common/math/big.go
```diff
@@ -54,7 +54,7 @@ func NewHexOrDecimal256(x int64) *HexOrDecimal256 {
 // It is similar to UnmarshalText, but allows parsing real decimals too, not just
 // quoted decimal strings.
 func (i *HexOrDecimal256) UnmarshalJSON(input []byte) error {
-	if len(input) > 0 && input[0] == '"' {
+	if len(input) > 1 && input[0] == '"' {
 		input = input[1 : len(input)-1]
 	}
 	return i.UnmarshalText(input)
```

### common/math/integer.go
```diff
@@ -46,7 +46,7 @@ type HexOrDecimal64 uint64
 // It is similar to UnmarshalText, but allows parsing real decimals too, not just
 // quoted decimal strings.
 func (i *HexOrDecimal64) UnmarshalJSON(input []byte) error {
-	if len(input) > 0 && input[0] == '"' {
+	if len(input) > 1 && input[0] == '"' {
 		input = input[1 : len(input)-1]
 	}
 	return i.UnmarshalText(input)
```
