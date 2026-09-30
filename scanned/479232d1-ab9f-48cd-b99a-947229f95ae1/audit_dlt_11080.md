# [?] cannon: Prevent deadlock on pre-image reads

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2023-08-28
Source: https://github.com/kroma-network/kroma/commit/877fcf887668db890d2eb9d09909da83cee60f96
Type: security-commit

## Details
cannon: Prevent deadlock on pre-image reads

Reading a FileChannel that does not have a writer blocks
indefinitely. This occurs in cannon whenever the pre-image oracle
server shuts down prematurely. We add a new io.ReadWriter that can
detect when a FileChannel would otherwise block indefinitely.

## Patch
### cannon/cmd/run.go
```diff
@@ -1,6 +1,7 @@
 package cmd
 
 import (
+	"context"
 	"fmt"
 	"os"
 	"os/exec"
@@ -112,11 +113,15 @@ func (rk rawKey) PreimageKey() [32]byte {
 }
 
 type ProcessPreimageOracle struct {
-	pCl *preimage.OracleClient
-	hCl *preimage.HintWriter
-	cmd *exec.Cmd
+	pCl      *preimage.OracleClient
+	hCl      *preimage.HintWriter
+	cmd      *exec.Cmd
+	waitErr  chan error
+	cancelIO context.CancelCauseFunc
 }
 
+const clientPollTimeout = time.Second * 15
+
 func NewProcessPreimageOracle(name string, args []string) (*ProcessPreimageOracle, error) {
 	if name == "" {
 		return &ProcessPreimageOracle{}, nil
@@ -140,10 +145,18 @@ func NewProcessPreimageOracle(name string, args []string) (*ProcessPreimageOracl
 		pOracleRW.Reader(),
 		pOracleRW.Writer(),
 	}
+
+	// Note that the client file descriptors are not closed when the pre-image server exits.
+	// So we use the FilePoller to ensure that we don't get stuck in a blocking read/write.
+	ctx, cancelIO := context.WithCancelCause(context.Background())
+	preimageClientIO := preimage.NewFilePoller(ctx, pClientRW, clientPollTimeout)
+	hostClientIO := preimage.NewFilePoller(ctx, hClientRW, clientPollTimeout)
 	out := &ProcessPreimageOracle{
-		pCl: preimage.NewOracleClient(pClientRW),
-		hCl: preimage.NewHintWriter(hClientRW),
-		cmd: cmd,
+		pCl:      preimage.NewOracleClient(preimageClientIO),
+		hCl:      preimage.NewHintWriter(hostClientIO),
+		cmd:      cmd,
+		waitErr:  make(chan error),
+		cancelIO: cancelIO,
 	}
 	return out, nil
 }
@@ -166,23 +179,37 @@ func (p *ProcessPreimageOracle) Start() error {
 	if p.cmd == nil {
 		return nil
 	}
-	return p.cmd.Start()
+	err := p.cmd.Start()
+	go p.wait()
+	return err
 }
 
 func (p *ProcessPreimageOracle) Close() error {
 	if p.cmd == nil {
 		return nil
 	}
+	// We first check if the process has already exited before signaling.
+	// Note: This is a teeny bit racy since the process could exit after the check
+	// above and another process is assigned the same pid.
+	select {
+	case err := <-p.waitErr:
+		return err
+	case <-time.After(time.Second * 1):
+		// give the wait goroutine time to reap process
+	}
 	_ = p.cmd.Process.Signal(os.Interrupt)
-	// Go 1.20 feature, to introduce later
-	//p.cmd.WaitDelay = time.Second * 10
+	return <-p.waitErr
+}
+
+func (p *ProcessPreimageOracle) wait() {
 	err := p.cmd.Wait()
-	if err, ok := err.(*exec.ExitError); ok {
-		if err.Success() {
-			return nil
-		}
+	var waitErr error
+	if err, ok := err.(*exec.ExitError); !ok || !err.Success() {
+		waitErr = err
 	}
-	return err
+	p.cancelIO(fmt.Errorf("%w: pre-image server has exited", waitErr))
+	p.waitErr <- waitErr
+	close(p.waitErr)
 }
 
 type StepFn func(proof bool) (*mipsevm.StepWitness, error)
```

### op-preimage/filepoller.go
```diff
@@ -0,0 +1,68 @@
+package preimage
+
+import (
+	"context"
+	"errors"
+	"os"
+	"time"
+)
+
+// FilePoller is a ReadWriteCloser that polls the underlying file channel for reads and writes
+// until its context is done. This is useful in detecting when the other end of a
+// blocking pre-image channel is no longer available.
+type FilePoller struct {
+	File        FileChannel
+	ctx         context.Context
+	pollTimeout time.Duration
+}
+
+// NewFilePoller returns a FilePoller that polls the underlying file channel for reads and writes until
+// the provided ctx is done. The poll timeout is the maximum amount of time to wait for I/O before
+// the operation is halted and the context is checked for cancellation.
+func NewFilePoller(ctx context.Context, f FileChannel, pollTimeout time.Duration) *FilePoller {
+	return &FilePoller{File: f, ctx: ctx, pollTimeout: pollTimeout}
+}
+
+func (f *FilePoller) Read(b []byte) (int, error) {
+	var read int
+	for {
+		if err := f.File.Reader().SetReadDeadline(time.Now().Add(f.pollTimeout)); err != nil {
+			panic(err)
+		}
+		n, err := f.File.Read(b[read:])
+		if errors.Is(err, os.ErrDeadlineExceeded) {
+			if cerr := f.ctx.Err(); cerr != nil {
+				return read, cerr
+			}
+		} else {
+			read += n
+			if read >= len(b) {
+				return read, err
+			}
+		}
+	}
+}
+
+func (f *FilePoller) Write(b []byte) (int, error) {
+	var written int
+	for {
+		if err := f.File.Writer().SetWriteDeadline(time.Now().Add(f.pollTimeout)); err != nil {
+			panic(err)
+		}
+		n, err := f.File.Write(b[written:])
+		if errors.Is(err, os.ErrDeadlineExceeded) {
+			if cerr := f.ctx.Err(); cerr != nil {
+				return written, cerr
+			}
+		} else {
+			written += n
+			if written >= len(b) {
+				return written, err
+			}
+		}
+	}
+}
+
+func (p *FilePoller) Close() error {
+	return p.File.Close()
+}
```

### op-preimage/filepoller_test.go
```diff
@@ -0,0 +1,86 @@
+package preimage
+
+import (
+	"context"
+	"testing"
+	"time"
+
+	"github.com/stretchr/testify/require"
+)
+
+func TestFilePoller_Read(t *testing.T) {
+	chanA, chanB, err := CreateBidirectionalChannel()
+	require.NoError(t, err)
+	ctx := context.Background()
+	chanAPoller := NewFilePoller(ctx, chanA, time.Millisecond*100)
+
+	go func() {
+		chanB.Write([]byte("hello"))
+		time.Sleep(time.Second * 1)
+		chanB.Write([]byte("world"))
+	}()
+	var buf [10]byte
+	n, err := chanAPoller.Read(buf[:])
+	require.Equal(t, 10, n)
+	require.NoError(t, err)
+}
+
+func TestFilePoller_Write(t *testing.T) {
+	chanA, chanB, err := CreateBidirectionalChannel()
+	require.NoError(t, err)
+	ctx := context.Background()
+	chanAPoller := NewFilePoller(ctx, chanA, time.Millisecond*100)
+
+	bufch := make(chan []byte, 1)
+	go func() {
+		var buf [10]byte
+		chanB.Read(buf[:5])
+		time.Sleep(time.Second * 1)
+		chanB.Read(buf[5:])
+		bufch <- buf[:]
+		close(bufch)
+	}()
+	buf := []byte("helloworld")
+	n, err := chanAPoller.Write(buf)
+	require.Equal(t, 10, n)
+	require.NoError(t, err)
+	select {
+	case <-time.After(time.Second * 60):
+		t.Fatal("timed out waiting for read")
+	case readbuf := <-bufch:
+		require.Equal(t, buf, readbuf)
+	}
+}
+
+func TestFilePoller_ReadCancel(t *testing.T) {
+	chanA, chanB, err := CreateBidirectionalChannel()
+	require.NoError(t, err)
+	ctx, cancel := context.WithCancel(context.Background())
+	chanAPoller := NewFilePoller(ctx, chanA, time.Millisecond*100)
+
+	go func() {
+		chanB.Write([]byte("hello"))
+		cancel()
+	}()
+	var buf [10]byte
+	n, err := chanAPoller.Read(buf[:])
+	require.Equal(t, 5, n)
+	require.ErrorIs(t, err, context.Canceled)
+}
+
+func TestFilePoller_WriteCancel(t *testing.T) {
+	chanA, chanB, err := CreateBidirectionalChannel()
+	require.NoError(t, err)
+	ctx, cancel := context.WithCancel(context.Background())
+	chanAPoller := NewFilePoller(ctx, chanA, time.Millisecond*100)
+
+	go func() {
+		var buf [5]byte
+		chanB.Read(buf[:])
+		cancel()
+	}()
+	// use a large buffer to overflow the kernel buffer provided to pipe(2) so the write actually blocks
+	buf := make([]byte, 1024*1024)
+	_, err = chanAPoller.Write(buf)
+	require.ErrorIs(t, err, context.Canceled)
+}
```
