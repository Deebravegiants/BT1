# [?] data race fix

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2018-10-29
Source: https://github.com/0xsoniclabs/sonic/commit/6200ffc03a964953a593680b6b519431576a4768
Type: security-commit

## Details
data race fix

## Patch
### src/proxy/grpc_lachesis.go
```diff
@@ -4,7 +4,8 @@ import (
 	"context"
 	"errors"
 	"io"
-	"sync"
+	"sync/atomic"
+	"time"
 
 	"github.com/rs/xid"
 	"github.com/sirupsen/logrus"
@@ -16,8 +17,8 @@ import (
 )
 
 var (
-	ErrDisconnected = errors.New("client disconnected")
-	ErrTryAgain     = errors.New("try again after reconnect")
+	ZeroTime        = time.Date(0, time.January, 0, 0, 0, 0, 0, time.Local)
+	ErrConnShutdown = errors.New("client disconnected")
 )
 
 type GrpcLachesisProxy struct {
@@ -28,11 +29,9 @@ type GrpcLachesisProxy struct {
 
 	addr             string
 	shutdown         chan struct{}
-	reconnect_ticket chan struct{}
-	reconnect_wg     *sync.WaitGroup
+	reconnect_ticket chan time.Time
 	conn             *grpc.ClientConn
-	client           internal.LachesisNodeClient
-	stream           internal.LachesisNode_ConnectClient
+	stream           atomic.Value
 }
 
 func NewGrpcLachesisProxy(addr string, logger *logrus.Logger) (*GrpcLachesisProxy, error) {
@@ -44,15 +43,14 @@ func NewGrpcLachesisProxy(addr string, logger *logrus.Logger) (*GrpcLachesisProx
 	p := &GrpcLachesisProxy{
 		addr:             addr,
 		shutdown:         make(chan struct{}),
-		reconnect_ticket: make(chan struct{}, 1),
-		reconnect_wg:     &sync.WaitGroup{},
+		reconnect_ticket: make(chan time.Time, 1),
 		logger:           logger,
 		commitCh:         make(chan proto.Commit),
 		queryCh:          make(chan proto.SnapshotRequest),
 		restoreCh:        make(chan proto.RestoreRequest),
 	}
 
-	p.reconnect_ticket <- struct{}{}
+	p.reconnect_ticket <- time.Now()
 	err := p.reConnect()
 	if err != nil {
 		return nil, err
@@ -109,67 +107,75 @@ func (p *GrpcLachesisProxy) SubmitTx(tx []byte) error {
 
 func (p *GrpcLachesisProxy) sendToServer(data *internal.ToServer) (err error) {
 	for {
-		err = p.stream.Send(data)
+		err = p.getStream().Send(data)
 		if err == nil {
 			return
 		}
 		p.logger.Warnf("send to server err: %s", err)
 
 		err = p.reConnect()
-		if err == ErrDisconnected {
-			_ = p.stream.CloseSend()
+		if err == ErrConnShutdown {
 			return
 		}
 	}
 }
 
 func (p *GrpcLachesisProxy) recvFromServer() (data *internal.ToClient, err error) {
 	for {
-		data, err = p.stream.Recv()
+		data, err = p.getStream().Recv()
 		if err == nil {
 			return
 		}
 		p.logger.Warnf("recv from server err: %s", err)
 
 		err = p.reConnect()
-		if err == ErrDisconnected {
+		if err == ErrConnShutdown {
 			return
 		}
 	}
 }
 
 func (p *GrpcLachesisProxy) reConnect() (err error) {
-	select {
-	case <-p.reconnect_ticket:
-		p.reconnect_wg.Add(1)
-		defer func() {
-			p.reconnect_wg.Done()
-			p.reconnect_ticket <- struct{}{}
-		}()
-	default:
-		p.reconnect_wg.Wait()
-		return ErrTryAgain
+	disconn_time := time.Now()
+	connect_time := <-p.reconnect_ticket
+
+	if connect_time == ZeroTime {
+		p.reconnect_ticket <- ZeroTime
+		return ErrConnShutdown
+	}
+
+	if disconn_time.Before(connect_time) {
+		p.reconnect_ticket <- connect_time
+		return nil
 	}
 
 	select {
 	case <-p.shutdown:
+		p.getStream().CloseSend()
 		p.conn.Close()
-		return ErrDisconnected
+		p.reconnect_ticket <- ZeroTime
+		return ErrConnShutdown
 	default:
+		// see code below
 	}
 
 	p.conn, err = grpc.Dial(p.addr, grpc.WithInsecure())
 	if err != nil {
-		p.logger.Warnf("reconnect err: %s", err)
+		p.logger.Warnf("dial err: %s", err)
+		p.reconnect_ticket <- connect_time
 		return
 	}
 
-	p.client = internal.NewLachesisNodeClient(p.conn)
-
-	p.stream, err = p.client.Connect(context.TODO())
+	client := internal.NewLachesisNodeClient(p.conn)
+	stream, err := client.Connect(context.TODO())
 	if err != nil {
+		p.logger.Warnf("rpc Connect() err: %s", err)
+		p.reconnect_ticket <- connect_time
 		return
 	}
+
+	p.setStream(stream)
+	p.reconnect_ticket <- time.Now()
 	return
 }
 
@@ -187,10 +193,9 @@ func (p *GrpcLachesisProxy) listen_events() {
 			} else {
 				p.logger.Debugf("recv EOF: %s", err)
 			}
-
 			break
 		}
-
+		// block commit event
 		if b := event.GetBlock(); b != nil {
 			var pb poset.Block
 			err = pb.Unmarshal(b.Data)
@@ -206,7 +211,7 @@ func (p *GrpcLachesisProxy) listen_events() {
 			}
 			continue
 		}
-
+		// get snapshot query
 		if q := event.GetQuery(); q != nil {
 			uuid, err = xid.FromBytes(q.Uid)
 			if err == nil {
@@ -217,7 +222,7 @@ func (p *GrpcLachesisProxy) listen_events() {
 			}
 			continue
 		}
-
+		// restore event
 		if r := event.GetRestore(); r != nil {
 			uuid, err = xid.FromBytes(r.Uid)
 			if err == nil {
@@ -298,3 +303,11 @@ func newAnswer(uuid []byte, data []byte, err error) *internal.ToServer {
 		},
 	}
 }
+
+func (p *GrpcLachesisProxy) getStream() internal.LachesisNode_ConnectClient {
+	return p.stream.Load().(internal.LachesisNode_ConnectClient)
+}
+
+func (p *GrpcLachesisProxy) setStream(stream internal.LachesisNode_ConnectClient) {
+	p.stream.Store(stream)
+}
```

### src/proxy/grpc_test.go
```diff
@@ -15,10 +15,10 @@ var (
 	errTimeout = "time is over"
 )
 
-func TestGrpcConnection(t *testing.T) {
+func TestGrpcCalls(t *testing.T) {
 	addr := "127.0.0.1:9993"
 
-	s, err := NewGrpcAppProxy(addr, timeout/2, nil)
+	s, err := NewGrpcAppProxy(addr, timeout, nil)
 	assert.NoError(t, err)
 
 	c, err := NewGrpcLachesisProxy(addr, nil)
@@ -34,7 +34,7 @@ func TestGrpcConnection(t *testing.T) {
 		select {
 		case tx := <-s.SubmitCh():
 			assert.Equal(gold, tx)
-		case <-time.After(timeout):
+		case <-time.After(2 * timeout):
 			assert.Fail(errTimeout)
 		}
 	})
@@ -52,7 +52,7 @@ func TestGrpcConnection(t *testing.T) {
 					StateHash: gold,
 					Error:     nil,
 				}
-			case <-time.After(timeout):
+			case <-time.After(2 * timeout):
 				assert.Fail(errTimeout)
 			}
 		}()
@@ -75,7 +75,7 @@ func TestGrpcConnection(t *testing.T) {
 					Snapshot: gold,
 					Error:    nil,
 				}
-			case <-time.After(timeout):
+			case <-time.After(2 * timeout):
 				assert.Fail(errTimeout)
 			}
 		}()
@@ -97,7 +97,7 @@ func TestGrpcConnection(t *testing.T) {
 					StateHash: gold,
 					Error:     nil,
 				}
-			case <-time.After(timeout):
+			case <-time.After(2 * timeout):
 				assert.Fail(errTimeout)
 			}
 		}()
@@ -121,7 +121,7 @@ func TestGrpcReConnection(t *testing.T) {
 	assert.Nil(t, c)
 	assert.Error(t, err)
 
-	s, err := NewGrpcAppProxy(addr, timeout/2, nil)
+	s, err := NewGrpcAppProxy(addr, timeout, nil)
 	assert.NoError(t, err)
 
 	c, err = NewGrpcLachesisProxy(addr, nil)
@@ -137,7 +137,7 @@ func TestGrpcReConnection(t *testing.T) {
 		select {
 		case tx := <-s.SubmitCh():
 			assert.Equal(gold, tx)
-		case <-time.After(timeout):
+		case <-time.After(2 * timeout):
 			assert.Fail(errTimeout)
 		}
 
@@ -154,5 +154,4 @@ func TestGrpcReConnection(t *testing.T) {
 
 	err = c.Close()
 	assert.NoError(t, err)
-
 }
```
