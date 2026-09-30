# [?] update muxers, includes yamux deadlock fix

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2016-05-13
Source: https://github.com/libp2p/go-libp2p/commit/de1d6754171eaef9c1497b936adbd69b28a1808a
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

### package.json
```diff
@@ -109,9 +109,9 @@
       "version": "0.0.0"
     },
     {
-      "hash": "QmWo4w5EybXUjBn9L7nsBneEPcLArq6fDMBWEFJ2Qny6Eq",
+      "hash": "Qmb1US8uyZeEpMyc56wVZy2cDFdQjNFojAUYVCoo9ieTqp",
       "name": "go-stream-muxer",
-      "version": "0.0.0"
+      "version": "1.0.0"
     },
     {
       "hash": "QmaaC9QMYTQHCbMq3Ebr3uMaAR2ev4AVqMmsJpgQijAZbJ",
@@ -129,9 +129,9 @@
       "version": "0.0.0"
     },
     {
-      "hash": "Qmcq3bs1zXXoougbpTtLRp7AravkCGBkVyCqJxZRk5qdwo",
+      "hash": "QmduCCgTaLnxwwf9RFQy2PMUytrKcEH9msohtVxSBZUdgu",
       "name": "go-peerstream",
-      "version": "0.0.0"
+      "version": "1.0.0"
     },
     {
       "author": "whyrusleeping",
@@ -162,6 +162,24 @@
       "hash": "QmaLnS2kGBLuGZKJdT5KAyoWEtW3u8CS3h6YKCVge5ohD2",
       "name": "go-libp2p-transport",
       "version": "1.1.1"
+    },
+    {
+      "author": "whyrusleeping",
+      "hash": "QmYaeRqthWTco7oQF4dztuqA94P8JF36gVjd2z2eEqKfrh",
+      "name": "go-smux-yamux",
+      "version": "1.1.0"
+    },
+    {
+      "author": "whyrusleeping",
+      "hash": "QmVcmcQE9eX4HQ8QwhVXpoHt3ennG7d299NDYFq9D1Uqa1",
+      "name": "go-smux-multistream",
+      "version": "1.0.0"
+    },
+    {
+      "author": "whyrusleeping",
+      "hash": "QmWMKNLGkYJTZ4Tq3DQ8E9j86QaKvGjKgFzvLzGYXvW69Z",
+      "name": "go-smux-spdystream",
+      "version": "1.0.0"
     }
   ],
   "gxVersion": "0.4.0",
```
