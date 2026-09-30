# [?] fix: Fix race condition in privval shutdown (#5934)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-07-06
Source: https://github.com/cometbft/cometbft/commit/eabe04b9bfc4867fe491f9fced21fb04553c3fd5
Type: security-commit

## Details
fix: Fix race condition in privval shutdown (#5934)

---

Updates the privval RetrySignerClient to check on shutdown before
retrying.
Without this change it is possible to get into the following shutdown
state:
* Node is requesting a signature from a remote signer
* Shutdown happens on remote signer
* Shutdown happens on node


In this case we have to wait `retries × (timeoutAccept + timeout) ≈
155s` before the node will shut down.

With these changes we will wait a maximum of a single retry timeout
before seeing that `Close` has been called (~3s) and shutdown will
happen after that.

---------

Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -56,6 +56,8 @@
   ([\#5879](https://github.com/cometbft/cometbft/pull/5879))
 - `[consensus]` release cs.mtx before sending to statsMsgQueue
   ([\#5813](https://github.com/cometbft/cometbft/pull/5813))
+- `[privval]` preempt sleep retries in privval signer client
+  ([\#5934](https://github.com/cometbft/cometbft/pull/5934))
 
 ### IMPROVEMENTS
 
```

### node/node.go
```diff
@@ -4,6 +4,7 @@ import (
 	"bytes"
 	"context"
 	"fmt"
+	"io"
 	"net"
 	"net/http"
 	"os"
@@ -744,6 +745,16 @@ func (n *Node) OnStop() {
 			n.Logger.Error("Error closing indexerService", "err", err)
 		}
 	}
+	// Close the priv validator before stopping the reactors: sw.Stop waits on
+	// the consensus receiveRoutine, which can be stuck retrying a gone remote
+	// signer. Closing aborts that retry loop. (RetrySignerClient is not a
+	// service.Service, so the assertion below never fires for the socket client.)
+	if c, ok := n.privValidator.(io.Closer); ok {
+		if err := c.Close(); err != nil {
+			n.Logger.Error("Error closing private validator", "err", err)
+		}
+	}
+
 	// now stop the reactors
 	if err := n.sw.Stop(); err != nil {
 		n.Logger.Error("Error closing switch", "err", err)
```

### privval/retry_signer_client.go
```diff
@@ -2,6 +2,7 @@ package privval
 
 import (
 	"fmt"
+	"sync"
 	"time"
 
 	"github.com/cometbft/cometbft/crypto"
@@ -15,20 +16,37 @@ type RetrySignerClient struct {
 	next    *SignerClient
 	retries int
 	timeout time.Duration
+
+	quitOnce sync.Once
+	quit     chan struct{} // closed by Close to abort in-flight retry loops
 }
 
 // NewRetrySignerClient returns RetrySignerClient. If +retries+ is 0, the
 // client will be retrying each operation indefinitely.
 func NewRetrySignerClient(sc *SignerClient, retries int, timeout time.Duration) *RetrySignerClient {
-	return &RetrySignerClient{sc, retries, timeout}
+	return &RetrySignerClient{next: sc, retries: retries, timeout: timeout, quit: make(chan struct{})}
 }
 
 var _ types.PrivValidator = (*RetrySignerClient)(nil)
 
+// Close aborts any in-flight retry loop and closes the underlying client. Safe
+// to call more than once. The abort unblocks node shutdown, which waits on the
+// consensus receiveRoutine that signs synchronously.
 func (sc *RetrySignerClient) Close() error {
+	sc.quitOnce.Do(func() { close(sc.quit) })
 	return sc.next.Close()
 }
 
+// sleep waits for timeout, returning false if Close was called first.
+func (sc *RetrySignerClient) sleep() bool {
+	select {
+	case <-sc.quit:
+		return false
+	case <-time.After(sc.timeout):
+		return true
+	}
+}
+
 func (sc *RetrySignerClient) IsConnected() bool {
 	return sc.next.IsConnected()
 }
@@ -58,7 +76,9 @@ func (sc *RetrySignerClient) GetPubKey() (crypto.PubKey, error) {
 		if _, ok := err.(*RemoteSignerError); ok {
 			return nil, err
 		}
-		time.Sleep(sc.timeout)
+		if !sc.sleep() {
+			return nil, fmt.Errorf("aborted getting pubkey: %w", err)
+		}
 	}
 	return nil, fmt.Errorf("exhausted all attempts to get pubkey: %w", err)
 }
@@ -74,7 +94,9 @@ func (sc *RetrySignerClient) SignVote(chainID string, vote *cmtproto.Vote) error
 		if _, ok := err.(*RemoteSignerError); ok {
 			return err
 		}
-		time.Sleep(sc.timeout)
+		if !sc.sleep() {
+			return fmt.Errorf("aborted signing vote: %w", err)
+		}
 	}
 	return fmt.Errorf("exhausted all attempts to sign vote: %w", err)
 }
@@ -90,7 +112,9 @@ func (sc *RetrySignerClient) SignProposal(chainID string, proposal *cmtproto.Pro
 		if _, ok := err.(*RemoteSignerError); ok {
 			return err
 		}
-		time.Sleep(sc.timeout)
+		if !sc.sleep() {
+			return fmt.Errorf("aborted signing proposal: %w", err)
+		}
 	}
 	return fmt.Errorf("exhausted all attempts to sign proposal: %w", err)
 }
```

### privval/retry_signer_client_test.go
```diff
@@ -0,0 +1,46 @@
+package privval
+
+import (
+	"testing"
+	"time"
+
+	"github.com/stretchr/testify/require"
+
+	"github.com/cometbft/cometbft/crypto/ed25519"
+	"github.com/cometbft/cometbft/libs/log"
+	cmtproto "github.com/cometbft/cometbft/proto/tendermint/types"
+)
+
+// TestRetrySignerClientCloseAborts checks Close aborts an in-flight retry loop
+// instead of draining the full retry budget (which would wedge node shutdown).
+func TestRetrySignerClientCloseAborts(t *testing.T) {
+	// Listener with no remote signer ever dialing in: every attempt blocks in
+	// WaitConnection until timeoutAccept, then errors.
+	endpoint := newSignerListenerEndpoint(log.TestingLogger(), "tcp://127.0.0.1:0", testTimeoutReadWrite)
+	require.NoError(t, endpoint.Start())
+	t.Cleanup(func() { _ = endpoint.Stop() })
+
+	sc, err := NewSignerClient(endpoint, "chain-id")
+	require.NoError(t, err)
+
+	// Large budget: if Close didn't abort, this would take many seconds.
+	rsc := NewRetrySignerClient(sc, 100, 50*time.Millisecond)
+
+	done := make(chan error, 1)
+	go func() {
+		done <- rsc.SignVote("chain-id", &cmtproto.Vote{ValidatorAddress: ed25519.GenPrivKey().PubKey().Address()})
+	}()
+
+	// Let one attempt get underway, then close.
+	time.Sleep(100 * time.Millisecond)
+	require.NoError(t, rsc.Close())
+
+	select {
+	case err := <-done:
+		require.Error(t, err) // aborted, not signed
+	case <-time.After(testTimeoutAccept + 2*time.Second):
+		t.Fatal("SignVote did not abort after Close")
+	}
+
+	require.NotPanics(t, func() { _ = rsc.Close() }) // idempotent
+}
```
