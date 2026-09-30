# [?] fix(api): prevent panic in NetAPI during initialization

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-07-11
Source: https://github.com/kaiachain/kaia/commit/3a3d70d2494b33b08efdbcaddda2169a250d997b
Type: security-commit

## Details
fix(api): prevent panic in NetAPI during initialization

## Patch
### api/api_net.go
```diff
@@ -47,11 +47,17 @@ func (s *NetAPI) Listening() bool {
 
 // PeerCount returns the number of connected peers.
 func (s *NetAPI) PeerCount() hexutil.Uint {
+	if s.net == nil {
+		return 0
+	}
 	return hexutil.Uint(s.net.PeerCount())
 }
 
 // PeerCountByType returns the number of connected specific types of nodes.
 func (s *NetAPI) PeerCountByType() map[string]uint {
+	if s.net == nil {
+		return make(map[string]uint)
+	}
 	return s.net.PeerCountByType()
 }
 
```
