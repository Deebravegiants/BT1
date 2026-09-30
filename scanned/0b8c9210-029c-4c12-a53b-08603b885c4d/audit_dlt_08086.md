# [?] Fix comparator that could cause a panic

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2017-06-06
Source: https://github.com/btcsuite/btcd/commit/ef87de9d8888726bb77cc921a69e0ffddb885740
Type: security-commit

## Details
Fix comparator that could cause a panic

## Patch
### connmgr/tor.go
```diff
@@ -99,7 +99,7 @@ func TorLookupIP(host, proxy string) ([]net.IP, error) {
 		return nil, ErrTorInvalidProxyResponse
 	}
 	if buf[1] != 0 {
-		if int(buf[1]) > len(torStatusErrors) {
+		if int(buf[1]) >= len(torStatusErrors) {
 			return nil, ErrTorInvalidProxyResponse
 		} else if err := torStatusErrors[buf[1]]; err != nil {
 			return nil, err
```
