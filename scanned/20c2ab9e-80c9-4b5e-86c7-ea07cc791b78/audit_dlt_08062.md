# [?] swarm/storage/mru: HOTFIX - fix panic in Handler.update (#17313)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-08-07
Source: https://github.com/celo-org/celo-blockchain/commit/64a4e89504b683074077b54518633b76c59ab507
Type: security-commit

## Details
swarm/storage/mru: HOTFIX - fix panic in Handler.update (#17313)

## Patch
### swarm/storage/mru/handler.go
```diff
@@ -469,7 +469,7 @@ func (h *Handler) update(ctx context.Context, r *SignedResourceUpdate) (updateAd
 	log.Trace("resource update", "updateAddr", r.updateAddr, "lastperiod", r.period, "version", r.version, "data", chunk.SData, "multihash", r.multihash)
 
 	// update our resources map entry if the new update is older than the one we have, if we have it.
-	if rsrc != nil && r.period > rsrc.period || (rsrc.period == r.period && r.version > rsrc.version) {
+	if rsrc != nil && (r.period > rsrc.period || (rsrc.period == r.period && r.version > rsrc.version)) {
 		rsrc.period = r.period
 		rsrc.version = r.version
 		rsrc.data = make([]byte, len(r.data))
```
