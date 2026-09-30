# [?] fix: state-verifier: CLI panic: do not expose any commands

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2024-11-11
Source: https://github.com/neutron-org/neutron/commit/91db8dbb154fe4cb5365883d553b5b3a5a595eea
Type: security-commit

## Details
fix: state-verifier: CLI panic: do not expose any commands

## Patch
### x/state-verifier/module.go
```diff
@@ -82,9 +82,13 @@ func (AppModuleBasic) RegisterGRPCGatewayRoutes(clientCtx client.Context, mux *r
 	}
 }
 
-// GetTxCmd returns the root Tx command for the module. The subcommands of this root command are used by end-users to generate new transactions containing messages defined in the module
+// Do not expose any CLI commands for this module
+
 func (a AppModuleBasic) GetTxCmd() *cobra.Command {
-	return nil
+	return &cobra.Command{}
+}
+func (a AppModuleBasic) GetQueryCmd() *cobra.Command {
+	return &cobra.Command{}
 }
 
 // ----------------------------------------------------------------------------
```
