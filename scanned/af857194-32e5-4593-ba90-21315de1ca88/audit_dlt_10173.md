# [?] go/runtime/localstorage: Fix nil dereference after close

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2025-06-19
Source: https://github.com/oasisprotocol/oasis-core/commit/86ce07cb99ea56e7ccb533067d6c7204bd3f4020
Type: security-commit

## Details
go/runtime/localstorage: Fix nil dereference after close

## Patch
### .changelog/6231.bugfix.md
```diff
@@ -0,0 +1 @@
+go/runtime/localstorage: Fix nil dereference after close
```

### go/runtime/localstorage/localstorage.go
```diff
@@ -7,6 +7,7 @@ import (
 	"errors"
 	"fmt"
 	"path/filepath"
+	"sync"
 
 	"github.com/dgraph-io/badger/v4"
 	"github.com/dgraph-io/badger/v4/options"
@@ -39,6 +40,8 @@ type localStorage struct {
 
 	db *badger.DB
 	gc *cmnBadger.GCWorker
+
+	closeOnce sync.Once
 }
 
 func (s *localStorage) Get(key []byte) ([]byte, error) {
@@ -92,13 +95,15 @@ func (s *localStorage) Set(key, value []byte) error {
 }
 
 func (s *localStorage) Stop() {
-	s.gc.Stop()
-	if err := s.db.Close(); err != nil {
-		s.logger.Error("failed to close local storage",
-			"err", err,
-		)
-	}
-	s.db = nil
+	s.closeOnce.Do(func() {
+		s.gc.Stop()
+
+		if err := s.db.Close(); err != nil {
+			s.logger.Error("failed to close local storage",
+				"err", err,
+			)
+		}
+	})
 }
 
 // New creates new untrusted local storage.
```
