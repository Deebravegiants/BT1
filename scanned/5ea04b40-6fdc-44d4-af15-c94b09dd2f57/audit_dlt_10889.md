# [?] fix: consensus failure (#1320)

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2025-09-03
Source: https://github.com/vechain/thor/commit/9da72cadc9ba3419615b7a67afcabc6ee6812ca2
Type: security-commit

## Details
fix: consensus failure (#1320)

## Patch
### consensus/poa_validator.go
```diff
@@ -103,36 +103,37 @@ func (p *poaCacher) Handle(header *block.Header, receipts tx.Receipts) (any, err
 		return false
 	}()
 
-	// if no event emitted from Authority contract, it's believed that the candidates list not changed
-	if !hasAuthorityEvent {
-		// if no endorsor related transfer, or no event emitted from Params contract, the proposers list
-		// can be reused
-		hasEndorsorEvent := func() bool {
-			for _, r := range receipts {
-				for _, o := range r.Outputs {
-					for _, ev := range o.Events {
-						// after HAYABUSA, authorities are allowed to migrate to staker contract,
-						// so any staker contract event(AddValidation, StakeIncreased/Decreased/Withdrawn) will need to invalidate cache
-						if header.Number() >= p.forkConfig.HAYABUSA && ev.Address == builtin.Staker.Address {
-							return true
-						}
-						if ev.Address == builtin.Params.Address {
-							return true
-						}
+	if hasAuthorityEvent {
+		return nil, nil
+	}
+
+	// if no endorsor related transfer, or no event emitted from Params contract, the proposers list
+	// can be reused
+	hasEndorsorEvent := func() bool {
+		for _, r := range receipts {
+			for _, o := range r.Outputs {
+				for _, ev := range o.Events {
+					// after HAYABUSA, authorities are allowed to migrate to staker contract,
+					// so any staker contract event(AddValidation, StakeIncreased/Decreased/Withdrawn) will need to invalidate cache
+					if header.Number() >= p.forkConfig.HAYABUSA && ev.Address == builtin.Staker.Address {
+						return true
+					}
+					if ev.Address == builtin.Params.Address {
+						return true
 					}
-					for _, t := range o.Transfers {
-						if p.candidates.IsEndorsor(t.Sender) || p.candidates.IsEndorsor(t.Recipient) {
-							return true
-						}
+				}
+				for _, t := range o.Transfers {
+					if p.candidates.IsEndorsor(t.Sender) || p.candidates.IsEndorsor(t.Recipient) {
+						return true
 					}
 				}
 			}
-			return false
-		}()
-
-		if hasEndorsorEvent {
-			p.candidates.InvalidateCache()
 		}
+		return false
+	}()
+
+	if hasEndorsorEvent {
+		p.candidates.InvalidateCache()
 	}
 
 	return p.candidates, nil
```

### consensus/poa_validator_test.go
```diff
@@ -365,6 +365,54 @@ func TestAuthorityCacheHandler_WithEndorsorTransfers(t *testing.T) {
 	assert.NoError(t, err)
 }
 
+func TestAuthorityCacheHandler_WithAuthoritySetEvent(t *testing.T) {
+	mockForkConfig := &thor.ForkConfig{}
+
+	candidateList := []*authority.Candidate{
+		{
+			NodeMaster: thor.BytesToAddress([]byte("master1")),
+			Endorsor:   thor.BytesToAddress([]byte("endorsor1")),
+			Identity:   thor.BytesToBytes32([]byte("identity1")),
+			Active:     true,
+		},
+	}
+
+	candidates := poa.NewCandidates(candidateList)
+
+	header := new(block.Builder).
+		ParentID(thor.BytesToBytes32([]byte("parent123"))).
+		Timestamp(1000).
+		GasLimit(1000000).
+		GasUsed(0).
+		TotalScore(0).
+		StateRoot(thor.Bytes32{}).
+		ReceiptsRoot(thor.Bytes32{}).
+		Beneficiary(thor.Address{}).
+		Build().Header()
+
+	receipts := tx.Receipts{
+		&tx.Receipt{
+			Outputs: []*tx.Output{
+				{
+					Events: tx.Events{
+						{
+							Address: builtin.Authority.Address,
+							Topics: []thor.Bytes32{
+								thor.BytesToBytes32([]byte("authority_set")),
+							},
+						},
+					},
+				},
+			},
+		},
+	}
+
+	cacher := &poaCacher{candidates, mockForkConfig}
+	output, err := cacher.Handle(header, receipts)
+	assert.NoError(t, err)
+	assert.Nil(t, output)
+}
+
 func TestAuthorityCacheHandler_WithMultipleEvents(t *testing.T) {
 	mockForkConfig := &thor.ForkConfig{}
 
```
