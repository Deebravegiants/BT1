# [?] Fix race condition

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2022-11-07
Source: https://github.com/NethermindEth/juno/commit/5d7d07308f8054947abd1472af113b36b60ba1a1
Type: security-commit

## Details
Fix race condition

## Patch
### cmd/juno/juno.go
```diff
@@ -103,7 +103,7 @@ func NewCmd(newNodeFn juno.NewStarkNetNodeFn, quit <-chan os.Signal) *cobra.Comm
 		shutDownErrCh := make(chan error)
 		go func() {
 			<-quit
-			if err = StarkNetNode.Shutdown(); err != nil {
+			if err := StarkNetNode.Shutdown(); err != nil {
 				shutDownErrCh <- err
 			}
 			close(shutDownErrCh)
```

### cmd/juno/juno_test.go
```diff
@@ -4,6 +4,7 @@ import (
 	"bytes"
 	"io/ioutil"
 	"os"
+	"sync"
 	"syscall"
 	"testing"
 	"time"
@@ -16,6 +17,7 @@ import (
 )
 
 type spyJuno struct {
+	sync.RWMutex
 	cfg   *juno.Config
 	calls []string
 	exit  chan struct{}
@@ -26,13 +28,17 @@ func newSpyJuno(junoCfg *juno.Config) (juno.StarkNetNode, error) {
 }
 
 func (s *spyJuno) Run() error {
+	s.Lock()
 	s.calls = append(s.calls, "run")
+	s.Unlock()
 	<-s.exit
 	return nil
 }
 
 func (s *spyJuno) Shutdown() error {
+	s.Lock()
 	s.calls = append(s.calls, "shutdown")
+	s.Unlock()
 	s.exit <- struct{}{}
 	return nil
 }
```
