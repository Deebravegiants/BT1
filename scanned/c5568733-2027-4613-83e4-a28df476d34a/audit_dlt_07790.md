# [?] fix panic (#12277)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2023-04-14
Source: https://github.com/OffchainLabs/prysm/commit/f376427adda754b0260baddc7ce7c4257c2dc130
Type: security-commit

## Details
fix panic (#12277)

## Patch
### beacon-chain/builder/service.go
```diff
@@ -77,7 +77,8 @@ func (s *Service) Start() {
 }
 
 // Stop halts the service.
-func (*Service) Stop() error {
+func (s *Service) Stop() error {
+	s.cancel()
 	return nil
 }
 
@@ -89,6 +90,9 @@ func (s *Service) SubmitBlindedBlock(ctx context.Context, b interfaces.ReadOnlyS
 	defer func() {
 		submitBlindedBlockLatency.Observe(float64(time.Since(start).Milliseconds()))
 	}()
+	if s.c == nil {
+		return nil, ErrNoBuilder
+	}
 
 	return s.c.SubmitBlindedBlock(ctx, b)
 }
@@ -101,6 +105,9 @@ func (s *Service) GetHeader(ctx context.Context, slot primitives.Slot, parentHas
 	defer func() {
 		getHeaderLatency.Observe(float64(time.Since(start).Milliseconds()))
 	}()
+	if s.c == nil {
+		return nil, ErrNoBuilder
+	}
 
 	return s.c.GetHeader(ctx, slot, parentHash, pubKey)
 }
@@ -124,6 +131,9 @@ func (s *Service) RegisterValidator(ctx context.Context, reg []*ethpb.SignedVali
 	defer func() {
 		registerValidatorLatency.Observe(float64(time.Since(start).Milliseconds()))
 	}()
+	if s.c == nil {
+		return ErrNoBuilder
+	}
 
 	idxs := make([]primitives.ValidatorIndex, 0)
 	msgs := make([]*ethpb.ValidatorRegistrationV1, 0)
```

### beacon-chain/builder/service_test.go
```diff
@@ -37,3 +37,18 @@ func Test_RegisterValidator(t *testing.T) {
 	require.NoError(t, s.RegisterValidator(ctx, []*eth.SignedValidatorRegistrationV1{{Message: &eth.ValidatorRegistrationV1{Pubkey: pubkey[:], FeeRecipient: feeRecipient[:]}}}))
 	assert.Equal(t, true, builder.RegisteredVals[pubkey])
 }
+
+func Test_BuilderMethodsWithouClient(t *testing.T) {
+	s, err := NewService(context.Background())
+	require.NoError(t, err)
+	assert.Equal(t, false, s.Configured())
+
+	_, err = s.GetHeader(context.Background(), 0, [32]byte{}, [48]byte{})
+	assert.ErrorContains(t, ErrNoBuilder.Error(), err)
+
+	_, err = s.SubmitBlindedBlock(context.Background(), nil)
+	assert.ErrorContains(t, ErrNoBuilder.Error(), err)
+
+	err = s.RegisterValidator(context.Background(), nil)
+	assert.ErrorContains(t, ErrNoBuilder.Error(), err)
+}
```
