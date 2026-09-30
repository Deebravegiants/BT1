# [?] p2p: fix array out of bounds issue (#23165)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-07-06
Source: https://github.com/ethereum/go-ethereum/commit/5afc82de6e617f8613577401b0e9e612703b97b6
Type: security-commit

## Details
p2p: fix array out of bounds issue (#23165)

## Patch
### p2p/peer_error.go
```diff
@@ -89,7 +89,7 @@ var discReasonToString = [...]string{
 }
 
 func (d DiscReason) String() string {
-	if len(discReasonToString) < int(d) {
+	if len(discReasonToString) <= int(d) {
 		return fmt.Sprintf("unknown disconnect reason %d", d)
 	}
 	return discReasonToString[d]
```
