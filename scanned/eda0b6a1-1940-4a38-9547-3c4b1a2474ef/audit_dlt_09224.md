# [?] fix: avoid panic on short hash

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2021-07-30
Source: https://github.com/ipfs/kubo/commit/0858dc62aa7303c0da67289eee590013730c631b
Type: security-commit

## Details
fix: avoid panic on short hash

(caught higher up but should still be fixed)

## Patch
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
