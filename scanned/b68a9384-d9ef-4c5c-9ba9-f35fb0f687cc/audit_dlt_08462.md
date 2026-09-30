# [?] fix(service/header): prevent deadlocks and panics in store by checking if store is closed with writeDn chan

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2022-02-13
Source: https://github.com/celestiaorg/celestia-node/commit/ec28b6d31007478142395a6a8f8289e3e5e8cd49
Type: security-commit

## Details
fix(service/header): prevent deadlocks and panics in store by checking if store is closed with writeDn chan

## Patch
### service/header/store.go
```diff
@@ -19,6 +19,9 @@ var (
 	DefaultIndexCacheSize = 2048
 )
 
+// errStoppedStore is returned on operations over stopped store
+var errStoppedStore = errors.New("header: stopped store")
+
 // store implement Store interface for ExtendedHeader over Datastore.
 type store struct {
 	// header storing
@@ -110,6 +113,11 @@ func (s *store) Start(ctx context.Context) error {
 }
 
 func (s *store) Stop(ctx context.Context) error {
+	select {
+	case <-s.writesDn:
+		return errStoppedStore
+	default:
+	}
 	// signal to prevent further writes to Store
 	s.writes <- nil
 	select {
@@ -246,6 +254,8 @@ func (s *store) Append(ctx context.Context, headers ...*ExtendedHeader) error {
 		// we return an error here after writing,
 		// as there might be an invalid header in between of a given range
 		return err
+	case <-s.writesDn:
+		return errStoppedStore
 	case <-ctx.Done():
 		return ctx.Err()
 	}
```
