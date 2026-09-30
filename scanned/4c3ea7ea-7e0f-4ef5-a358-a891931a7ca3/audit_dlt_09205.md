# [?] update mdns to version with fixed race condition

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2016-09-29
Source: https://github.com/libp2p/go-libp2p/commit/5b6ab8c326945709487f9e35950a5a14ff24804b
Type: security-commit

## Details
update mdns to version with fixed race condition

## Patch
### p2p/discovery/mdns.go
```diff
@@ -10,13 +10,13 @@ import (
 	"sync"
 	"time"
 
-	"github.com/cryptix/mdns"
 	"github.com/ipfs/go-libp2p-peer"
 	pstore "github.com/ipfs/go-libp2p-peerstore"
 	logging "github.com/ipfs/go-log"
 	ma "github.com/jbenet/go-multiaddr"
 	manet "github.com/jbenet/go-multiaddr-net"
 	"github.com/libp2p/go-libp2p/p2p/host"
+	"github.com/whyrusleeping/mdns"
 )
 
 var log = logging.Logger("mdns")
```

### package.json
```diff
@@ -14,9 +14,9 @@
       "version": "0.0.0"
     },
     {
-      "hash": "QmSscYPCcE1H3UQr2tnsJ2a9dK9LsHTBGgP71VW6fz67e5",
+      "hash": "QmZ6K4wx6uDZLPEjcDbHErMV1qGjSbcNrck3PqYSRhkrAN",
       "name": "mdns",
-      "version": "0.0.0"
+      "version": "0.1.0"
     },
     {
       "hash": "QmRQhVisS8dmPbjBUthVkenn81pBxrx1GxE281csJhm2vL",
@@ -202,4 +202,3 @@
   "releaseCmd": "git commit -a -m \"gx publish $VERSION\"",
   "version": "3.5.4"
 }
-
```
