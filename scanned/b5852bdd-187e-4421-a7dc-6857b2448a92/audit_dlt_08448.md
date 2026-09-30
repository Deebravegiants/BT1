# [?] fix(cel-shed): prevent panic on missing root hash (#4809)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2026-03-24
Source: https://github.com/celestiaorg/celestia-node/commit/8a784915e9fd92be22815e2aa8a50a060a7e94a2
Type: security-commit

## Details
fix(cel-shed): prevent panic on missing root hash (#4809)

Co-authored-by: Vlad <13818348+walldiss@users.noreply.github.com>

## Patch
### cmd/cel-shed/hash_presence.go
```diff
@@ -32,6 +32,10 @@ var hashCmd = &cobra.Command{
 			return err
 		}
 
+		if len(args) == 0 {
+			return fmt.Errorf("root hash argument is required")
+		}
+
 		rootHash, err := parseHash(args[0])
 		if err != nil {
 			return err
```
