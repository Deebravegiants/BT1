# [?] avoid deadlock while logging error about deadlock (#1362)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-01-22
Source: https://github.com/algorand/go-algorand/commit/2f583a03576cbca30ec6eef413d4dcd5fd5c3667
Type: security-commit

## Details
avoid deadlock while logging error about deadlock (#1362)

Previously algod would deadlock when trying to log an error about recursive locking. This PR addresses this issue be moving the logging into a separate go routine.

## Patch
### daemon/algod/deadlockLogger.go
```diff
@@ -38,12 +38,16 @@ func (logger *dumpLogger) dump() {
 
 var logger = dumpLogger{Logger: logging.Base(), Buffer: bytes.NewBuffer(make([]byte, 0))}
 
+var deadlockPanic func()
+
 func setupDeadlockLogger() {
+	deadlockPanic = func() {
+		logger.Panic("potential deadlock detected")
+	}
+
 	deadlock.Opts.LogBuf = logger
 	deadlock.Opts.OnPotentialDeadlock = func() {
-		logger.dump()
-
-		// Capture all goroutine stacks and log to stderr
+		// Capture all goroutine stacks
 		var buf []byte
 		bufferSize := 256 * 1024
 		for {
@@ -53,7 +57,12 @@ func setupDeadlockLogger() {
 			}
 			bufferSize *= 2
 		}
-		fmt.Fprintln(os.Stderr, string(buf))
-		logger.Panic("potential deadlock detected")
+
+		// Run this code in a separate goroutine because it might grab locks.
+		go func() {
+			logger.dump()
+			fmt.Fprintln(os.Stderr, string(buf))
+			deadlockPanic()
+		}()
 	}
 }
```

### daemon/algod/deadlock_test.go
```diff
@@ -0,0 +1,57 @@
+// Copyright (C) 2019-2021 Algorand, Inc.
+// This file is part of go-algorand
+//
+// go-algorand is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Affero General Public License as
+// published by the Free Software Foundation, either version 3 of the
+// License, or (at your option) any later version.
+//
+// go-algorand is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
+// GNU Affero General Public License for more details.
+//
+// You should have received a copy of the GNU Affero General Public License
+// along with go-algorand.  If not, see <https://www.gnu.org/licenses/>.
+
+package algod
+
+import (
+	"fmt"
+	"testing"
+	"time"
+
+	"github.com/algorand/go-deadlock"
+
+	"github.com/algorand/go-algorand/crypto"
+	"github.com/algorand/go-algorand/logging"
+)
+
+func TestDeadlockLogging(t *testing.T) {
+	logFn := fmt.Sprintf("/tmp/test.%s.%d.log", t.Name(), crypto.RandUint64())
+	archiveFn := fmt.Sprintf("%s.archive", logFn)
+
+	l := logging.Base()
+	logWriter := logging.MakeCyclicFileWriter(logFn, archiveFn, 65536, time.Hour)
+	l.SetOutput(logWriter)
+
+	setupDeadlockLogger()
+
+	deadlockCh := make(chan struct{})
+	deadlockPanic = func() {
+		close(deadlockCh)
+	}
+
+	var mu deadlock.RWMutex
+	defer func() {
+		r := recover()
+		if r != nil {
+			fmt.Printf("Recovered: %v\n", r)
+		}
+	}()
+
+	mu.RLock()
+	mu.RLock()
+
+	_ = <- deadlockCh
+}
```
