# [?] fix: when the relay client is disabled and hole punching is left in its default state silently turn off hole punching instead of panicking

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2022-05-03
Source: https://github.com/ipfs/kubo/commit/346fd9d8544152e906da9eede6f7cde93a5810d5
Type: security-commit

## Details
fix: when the relay client is disabled and hole punching is left in its default state silently turn off hole punching instead of panicking

## Patch
### core/node/libp2p/relay.go
```diff
@@ -71,7 +71,11 @@ func HolePunching(flag config.Flag, hasRelayClient bool) func() (opts Libp2pOpts
 	return func() (opts Libp2pOpts, err error) {
 		if flag.WithDefault(true) {
 			if !hasRelayClient {
-				log.Fatal("Failed to enable `Swarm.EnableHolePunching`, it requires `Swarm.RelayClient.Enabled` to be true.")
+				// If hole punching is explicitly enabled but the relay client is disabled then panic,
+				// otherwise just silently disable hole punching
+				if flag != config.Default {
+					log.Fatal("Failed to enable `Swarm.EnableHolePunching`, it requires `Swarm.RelayClient.Enabled` to be true.")
+				}
 				return
 			}
 			opts.Opts = append(opts.Opts, libp2p.EnableHolePunching())
```
