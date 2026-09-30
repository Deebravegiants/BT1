# [?] fix: fixes #168 adds context to a non-deterministic compilation error in the Assert object

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2021-11-08
Source: https://github.com/Consensys-Incorporated/gnark/commit/d0d7ce778f5309c20b36c902f790602b04616777
Type: security-commit

## Details
fix: fixes #168 adds context to a non-deterministic compilation error in the Assert object

## Patch
### test/assert.go
```diff
@@ -366,7 +366,7 @@ func (assert *Assert) compile(circuit frontend.Circuit, curveID ecc.ID, backendI
 
 	_ccs, err := frontend.Compile(curveID, backendID, circuit, compileOpts...)
 	if err != nil {
-		return nil, err
+		return nil, fmt.Errorf("%w: %v", ErrCompilationNotDeterministic, err)
 	}
 
 	if !reflect.DeepEqual(ccs, _ccs) {
```
