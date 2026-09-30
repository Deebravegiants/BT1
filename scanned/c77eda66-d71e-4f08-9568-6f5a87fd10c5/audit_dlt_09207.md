# [?] update muxers, includes yamux deadlock fix

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2016-05-13
Source: https://github.com/libp2p/go-libp2p/commit/936b1571c3f622092870c0d12d4b560284694b16
Type: security-commit

## Details
update muxers, includes yamux deadlock fix

## Patch
### p2p/net/swarm/swarm.go
```diff
@@ -22,11 +22,11 @@ import (
 	ma "github.com/jbenet/go-multiaddr"
 	ps "github.com/jbenet/go-peerstream"
 	pst "github.com/jbenet/go-stream-muxer"
-	psmss "github.com/jbenet/go-stream-muxer/multistream"
-	spdy "github.com/jbenet/go-stream-muxer/spdystream"
-	yamux "github.com/jbenet/go-stream-muxer/yamux"
 	"github.com/jbenet/goprocess"
 	goprocessctx "github.com/jbenet/goprocess/context"
+	psmss "github.com/whyrusleeping/go-smux-multistream"
+	spdy "github.com/whyrusleeping/go-smux-spdystream"
+	yamux "github.com/whyrusleeping/go-smux-yamux"
 	mafilter "github.com/whyrusleeping/multiaddr-filter"
 	context "golang.org/x/net/context"
 )
@@ -39,11 +39,11 @@ func init() {
 	msstpt := psmss.NewBlankTransport()
 
 	ymxtpt := &yamux.Transport{
-		AcceptBacklog:          8192,
+		AcceptBacklog:          1024,
 		ConnectionWriteTimeout: time.Second * 10,
 		KeepAliveInterval:      time.Second * 30,
 		EnableKeepAlive:        true,
-		MaxStreamWindowSize:    uint32(1024 * 256),
+		MaxStreamWindowSize:    uint32(1024 * 512),
 		LogOutput:              ioutil.Discard,
 	}
 
```
