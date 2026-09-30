# [?] src/node/core: fix data race in tests

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-05-22
Source: https://github.com/0xsoniclabs/sonic/commit/74bbe0ddd05746631bb4b2a3d814e4ccc95aa4a2
Type: security-commit

## Details
src/node/core: fix data race in tests

## Patch
### src/node/core.go
```diff
@@ -120,7 +120,7 @@ func (c *Core) Heights() map[string]int64 {
 func (c *Core) HeightsByID() map[uint64]int64 {
 	heights := make(map[uint64]int64)
 	for _, peer := range c.participants.ToPeerSlice() {
-		heights[peer.ID] = peer.Height
+		heights[peer.ID] = c.participants.GetHeightByPubKeyHex(peer.PubKeyHex)
 	}
 	return heights
 }
```
