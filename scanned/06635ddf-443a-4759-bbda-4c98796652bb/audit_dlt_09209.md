# [?] quick fix for OOM panic that has been plaguing us

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2015-05-02
Source: https://github.com/libp2p/go-libp2p/commit/333ef67d71bde9df1dc37c6570626b95f69565ac
Type: security-commit

## Details
quick fix for OOM panic that has been plaguing us

## Patch
### crypto/secio/rw.go
```diff
@@ -15,6 +15,10 @@ import (
 	context "github.com/ipfs/go-ipfs/Godeps/_workspace/src/golang.org/x/net/context"
 )
 
+const MaxMsgSize = 8 * 1024 * 1024
+
+var ErrMaxMessageSize = errors.New("attempted to read message larger than max size")
+
 // ErrMACInvalid signals that a MAC verification failed
 var ErrMACInvalid = errors.New("MAC verification failed")
 
@@ -130,6 +134,10 @@ func (r *etmReader) Read(buf []byte) (int, error) {
 		return 0, err
 	}
 
+	if fullLen > MaxMsgSize {
+		return 0, ErrMaxMessageSize
+	}
+
 	buf2 := buf
 	changed := false
 	// if not enough space, allocate a new buffer.
```
