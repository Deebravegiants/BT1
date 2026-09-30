# [?] fix: panic if multiple chain IDs passed (#10157)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-04-15
Source: https://github.com/bobanetwork/boba/commit/caaa0d081eaee9092cd80baf59bbbfc4e70ea5ab
Type: security-commit

## Details
fix: panic if multiple chain IDs passed (#10157)

## Patch
### op-chain-ops/cmd/op-upgrade/main.go
```diff
@@ -123,6 +123,11 @@ func entrypoint(ctx *cli.Context) error {
 	}
 
 	chainIDs := ctx.Uint64Slice("chain-ids")
+	if len(chainIDs) != 1 {
+		// This requirement is due to the `SYSTEM_CONFIG_START_BLOCK` environment variable
+		// that we read from in `op-chain-ops/upgrades/l1.go`
+		panic("op-upgrade currently only supports upgrading a single chain at a time")
+	}
 	deployConfig := ctx.Path("deploy-config")
 
 	// If no chain IDs are specified, upgrade all chains
```
