# [?] fix(header): Only bridge node should panic on data root mismatch in e… (#2558)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-08-11
Source: https://github.com/celestiaorg/celestia-node/commit/87e9500120c27450e264ab4ffd59c87e92186194
Type: security-commit

## Details
fix(header): Only bridge node should panic on data root mismatch in e… (#2558)

This PR fixes a DoS first discovered by @Wondertan and then secondarily
by @vgonkivs 🤠

Only bridge nodes should panic on receiving a header where the computed
data root does not match the DataHash in the RawHeader on ExtendedHeader
validation.

Resolves #2555

## Patch
### core/exchange.go
```diff
@@ -115,7 +115,7 @@ func (ce *Exchange) Get(ctx context.Context, hash libhead.Hash) (*header.Extende
 	// construct extended header
 	eh, err := ce.construct(ctx, &block.Header, comm, vals, eds)
 	if err != nil {
-		return nil, fmt.Errorf("constructing extended header for height %d: %w", &block.Height, err)
+		panic(fmt.Errorf("constructing extended header for height %d: %w", &block.Height, err))
 	}
 	// verify hashes match
 	if !bytes.Equal(hash, eh.Hash()) {
@@ -155,7 +155,7 @@ func (ce *Exchange) getExtendedHeaderByHeight(ctx context.Context, height *int64
 	// create extended header
 	eh, err := ce.construct(ctx, &b.Header, &b.Commit, &b.ValidatorSet, eds)
 	if err != nil {
-		return nil, fmt.Errorf("constructing extended header for height %d: %w", b.Header.Height, err)
+		panic(fmt.Errorf("constructing extended header for height %d: %w", b.Header.Height, err))
 	}
 
 	ctx = ipld.CtxWithProofsAdder(ctx, adder)
```

### core/header_test.go
```diff
@@ -41,11 +41,9 @@ func TestMakeExtendedHeaderForEmptyBlock(t *testing.T) {
 
 func TestMismatchedDataHash_ComputedRoot(t *testing.T) {
 	header := headertest.RandExtendedHeader(t)
-
 	header.DataHash = rand.Bytes(32)
 
-	panicFn := func() {
-		header.Validate() //nolint:errcheck
-	}
-	assert.Panics(t, panicFn)
+	err := header.Validate()
+	assert.Contains(t, err.Error(), "mismatch between data hash commitment from"+
+		" core header and computed data root")
 }
```

### core/listener.go
```diff
@@ -160,7 +160,7 @@ func (cl *Listener) handleNewSignedBlock(ctx context.Context, b types.EventDataS
 	// generate extended header
 	eh, err := cl.construct(ctx, &b.Header, &b.Commit, &b.ValidatorSet, eds)
 	if err != nil {
-		return fmt.Errorf("making extended header: %w", err)
+		panic(fmt.Errorf("making extended header: %w", err))
 	}
 
 	// attempt to store block data if not empty
```

### header/header.go
```diff
@@ -146,8 +146,8 @@ func (eh *ExtendedHeader) Validate() error {
 
 	// ensure data root from raw header matches computed root
 	if !bytes.Equal(eh.DAH.Hash(), eh.DataHash) {
-		panic(fmt.Sprintf("mismatch between data hash commitment from core header and computed data root "+
-			"at height %d: data hash: %X, computed root: %X", eh.Height(), eh.DataHash, eh.DAH.Hash()))
+		return fmt.Errorf("mismatch between data hash commitment from core header and computed data root "+
+			"at height %d: data hash: %X, computed root: %X", eh.Height(), eh.DataHash, eh.DAH.Hash())
 	}
 
 	// Make sure the header is consistent with the commit.
```
