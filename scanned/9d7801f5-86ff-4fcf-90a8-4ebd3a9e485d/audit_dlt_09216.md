# [?] fix(daemon): panic in kubo/daemon.go:595 (#10473)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2024-08-12
Source: https://github.com/ipfs/kubo/commit/a339e6e807fa5bde786e5a539b2958a15ea22125
Type: security-commit

## Details
fix(daemon): panic in kubo/daemon.go:595 (#10473)

## Patch
### cmd/ipfs/kubo/daemon.go
```diff
@@ -597,6 +597,7 @@ take effect.
 			cfg, err := cctx.GetConfig()
 			if err != nil {
 				log.Errorf("failed to access config: %s", err)
+				return
 			}
 			if len(cfg.Bootstrap) == 0 && len(cfg.Peering.Peers) == 0 {
 				// Skip peer check if Bootstrap and Peering lists are empty
@@ -607,10 +608,12 @@ take effect.
 			ipfs, err := coreapi.NewCoreAPI(node)
 			if err != nil {
 				log.Errorf("failed to access CoreAPI: %v", err)
+				return
 			}
 			peers, err := ipfs.Swarm().Peers(cctx.Context())
 			if err != nil {
 				log.Errorf("failed to read swarm peers: %v", err)
+				return
 			}
 			if len(peers) == 0 {
 				log.Error("failed to bootstrap (no peers found): consider updating Bootstrap or Peering section of your config")
```
