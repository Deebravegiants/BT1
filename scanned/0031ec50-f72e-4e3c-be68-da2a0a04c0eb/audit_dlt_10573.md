# [?] Merge pull request #81 from libp2p/fix/interned-nil-panic

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2019-06-01
Source: https://github.com/libp2p/go-libp2p/commit/bb7e91afdbbe34fede32dde4e9b892c9e6466a59
Type: security-commit

## Details
Merge pull request #81 from libp2p/fix/interned-nil-panic

set map in constructor

## Patch
### p2p/host/peerstore/pstoremem/metadata.go
```diff
@@ -29,7 +29,8 @@ var _ pstore.PeerMetadata = (*memoryPeerMetadata)(nil)
 
 func NewPeerMetadata() pstore.PeerMetadata {
 	return &memoryPeerMetadata{
-		ds: make(map[metakey]interface{}),
+		ds:       make(map[metakey]interface{}),
+		interned: make(map[string]interface{}),
 	}
 }
 
```
