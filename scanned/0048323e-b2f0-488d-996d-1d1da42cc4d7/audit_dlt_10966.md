# [?] fix: ToBits edge case for overflow=0

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2022-05-31
Source: https://github.com/Consensys-Incorporated/gnark/commit/164df2407d16387fba6863c966a937550c7966a6
Type: security-commit

## Details
fix: ToBits edge case for overflow=0

## Patch
### std/math/nonnative/variable.go
```diff
@@ -210,7 +210,9 @@ func (e *Element) ToBits() []frontend.Variable {
 	for i := 0; i < len(e.Limbs); i++ {
 		limbBits = bits.ToBinary(e.api, e.api.Add(e.Limbs[i], carry), bits.WithNbDigits(int(e.params.nbBits+e.overflow)))
 		fullBits = append(fullBits, limbBits[:e.params.nbBits]...)
-		carry = bits.FromBinary(e.api, limbBits[e.params.nbBits:])
+		if e.overflow > 0 {
+			carry = bits.FromBinary(e.api, limbBits[e.params.nbBits:])
+		}
 	}
 	fullBits = append(fullBits, limbBits[e.params.nbBits:e.params.nbBits+e.overflow]...)
 	return fullBits
```
