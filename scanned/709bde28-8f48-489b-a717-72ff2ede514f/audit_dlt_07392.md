# [?] fix: fix a potential out of bounds issue in fuse

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2020-01-28
Source: https://github.com/ipfs/kubo/commit/41aaf745ad8a4d4be7129fd4f8ea2cdc5521c4e4
Type: security-commit

## Details
fix: fix a potential out of bounds issue in fuse

We likely encountered a file that misreported its size. That or there was no bug
here and we hit an issue somewhere else. Regardless, there's no reason not to
simplify this code and this should fix the issue.

## Patch
### fuse/readonly/readonly_unix.go
```diff
@@ -257,13 +257,15 @@ func (s *Node) Read(ctx context.Context, req *fuse.ReadRequest, resp *fuse.ReadR
 	if err != nil {
 		return err
 	}
-
-	buf := resp.Data[:min(req.Size, int(int64(r.Size())-req.Offset))]
+	// Data has a capacity of Size
+	buf := resp.Data[:int(req.Size)]
 	n, err := io.ReadFull(r, buf)
-	if err != nil && err != io.EOF {
+	resp.Data = buf[:n]
+	switch err {
+	case nil, io.EOF, io.ErrUnexpectedEOF:
+	default:
 		return err
 	}
-	resp.Data = resp.Data[:n]
 	lm["res_size"] = n
 	return nil // may be non-nil / not succeeded
 }
@@ -287,10 +289,3 @@ type roNode interface {
 }
 
 var _ roNode = (*Node)(nil)
-
-func min(a, b int) int {
-	if a < b {
-		return a
-	}
-	return b
-}
```
