# [?] Fix Panic When Accessing State Frequently (#8928)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2021-05-24
Source: https://github.com/OffchainLabs/prysm/commit/503ec126e1438c403093dfabda68330d5c0d144d
Type: security-commit

## Details
Fix Panic When Accessing State Frequently (#8928)

* fix issue

* dont allocate for existence checks

* radek's review

## Patch
### beacon-chain/db/kv/state.go
```diff
@@ -128,11 +128,19 @@ func (s *Store) SaveStates(ctx context.Context, states []iface.ReadOnlyBeaconSta
 func (s *Store) HasState(ctx context.Context, blockRoot [32]byte) bool {
 	ctx, span := trace.StartSpan(ctx, "BeaconDB.HasState")
 	defer span.End()
-	enc, err := s.stateBytes(ctx, blockRoot)
+	hasState := false
+	err := s.db.View(func(tx *bolt.Tx) error {
+		bkt := tx.Bucket(stateBucket)
+		stBytes := bkt.Get(blockRoot[:])
+		if len(stBytes) > 0 {
+			hasState = true
+		}
+		return nil
+	})
 	if err != nil {
 		panic(err)
 	}
-	return len(enc) > 0
+	return hasState
 }
 
 // DeleteState by block root.
@@ -204,7 +212,16 @@ func (s *Store) stateBytes(ctx context.Context, blockRoot [32]byte) ([]byte, err
 	var dst []byte
 	err := s.db.View(func(tx *bolt.Tx) error {
 		bkt := tx.Bucket(stateBucket)
-		dst = bkt.Get(blockRoot[:])
+		stBytes := bkt.Get(blockRoot[:])
+		if len(stBytes) == 0 {
+			return nil
+		}
+		// Due to https://github.com/boltdb/bolt/issues/204, we need to
+		// allocate a byte slice separately in the transaction or there
+		// is the possibility of a panic when accessing that particular
+		// area of memory.
+		dst = make([]byte, len(stBytes))
+		copy(dst, stBytes)
 		return nil
 	})
 	return dst, err
```
