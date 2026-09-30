# [?] Merge pull request #8318 from ipfs/fix/path-panic

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2021-08-13
Source: https://github.com/ipfs/kubo/commit/7c76118b0b7026fba8357807e5a67b59fc2b684b
Type: security-commit

## Details
Merge pull request #8318 from ipfs/fix/path-panic

fix: avoid out of bounds error when rendering short hashes

## Patch
### core/corehttp/gateway_handler.go
```diff
@@ -412,11 +412,12 @@ func (i *gatewayHandler) getOrHeadHandler(w http.ResponseWriter, r *http.Request
 			size = humanize.Bytes(uint64(s))
 		}
 
-		hash := ""
-		if r, err := i.api.ResolvePath(r.Context(), ipath.Join(resolvedPath, dirit.Name())); err == nil {
-			// Path may not be resolved. Continue anyways.
-			hash = r.Cid().String()
+		resolved, err := i.api.ResolvePath(r.Context(), ipath.Join(resolvedPath, dirit.Name()))
+		if err != nil {
+			internalWebError(w, err)
+			return
 		}
+		hash := resolved.Cid().String()
 
 		// See comment above where originalUrlPath is declared.
 		di := directoryItem{
```

### core/corehttp/gateway_indexPage.go
```diff
@@ -75,6 +75,9 @@ func breadcrumbs(urlPath string, dnslinkOrigin bool) []breadcrumb {
 }
 
 func shortHash(hash string) string {
+	if len(hash) <= 8 {
+		return hash
+	}
 	return (hash[0:4] + "\u2026" + hash[len(hash)-4:])
 }
 
```
