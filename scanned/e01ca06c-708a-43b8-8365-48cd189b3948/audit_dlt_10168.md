# [?] go/common/node: Fix possible nil dereference

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2026-02-16
Source: https://github.com/oasisprotocol/oasis-core/commit/258280ff653407b532e3bb516928723cd9893bb1
Type: security-commit

## Details
go/common/node: Fix possible nil dereference

## Patch
### go/common/node/sgx.go
```diff
@@ -112,7 +112,7 @@ func (sc *SGXConstraints) ValidateBasic(cfg *TEEFeatures, isFeatureVersion242 bo
 	}
 
 	// Check for TDX enablement.
-	if !cfg.SGX.TDX && sc.Policy.PCS != nil && sc.Policy.PCS.TDX != nil {
+	if !cfg.SGX.TDX && sc.Policy != nil && sc.Policy.PCS != nil && sc.Policy.PCS.TDX != nil {
 		return fmt.Errorf("TDX policy not supported")
 	}
 
```

### go/common/node/sgx_test.go
```diff
@@ -68,6 +68,16 @@ func TestSGXConstraintsV1(t *testing.T) {
 	require.NoError(err, "ValidateBasic V1 SGX constraints")
 }
 
+func TestSGXConstraintsV1NilPolicy(t *testing.T) {
+	require := require.New(t)
+
+	sc := SGXConstraints{
+		Versioned: cbor.NewVersioned(1),
+	}
+	err := sc.ValidateBasic(&TEEFeatures{SGX: TEEFeaturesSGX{PCS: true}}, true)
+	require.NoError(err, "ValidateBasic V1 SGX constraints with nil policy")
+}
+
 func TestSGXAttestationV0(t *testing.T) {
 	require := require.New(t)
 
```
