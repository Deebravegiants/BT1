# [?] node/p2p: fix race condition in `AddrsFactory`

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2021-12-11
Source: https://github.com/celestiaorg/celestia-node/commit/dbfae9c5c55f63560fd418d25c919c2b87beb1dd
Type: security-commit

## Details
node/p2p: fix race condition in `AddrsFactory`

Copy `announce multi addresses` to separate array to avoid data race and return them with `listen multi addresses`.

Issue #286

## Patch
### node/p2p/addrs.go
```diff
@@ -47,7 +47,9 @@ func AddrsFactory(announce []string, noAnnounce []string) func() (_ p2pconfig.Ad
 
 		return func(maListen []ma.Multiaddr) (out []ma.Multiaddr) {
 			// combine maListen and maAnnounce addresses
-			maAnnounce = append(maAnnounce, maListen...)
+			out = make([]ma.Multiaddr, len(maAnnounce), len(maAnnounce)+len(maListen))
+			copy(out[:len(maAnnounce)], maAnnounce[:])
+
 			// filter out unneeded
 			for _, maddr := range maListen {
 				ok := maNoAnnounce[string(maddr.Bytes())]
```
