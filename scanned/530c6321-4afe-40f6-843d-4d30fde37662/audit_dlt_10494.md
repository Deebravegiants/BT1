# [?] register ICA query server, fix panics in params query cli (#666)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2021-12-23
Source: https://github.com/sei-protocol/sei-chain/commit/961f78770a0e53edf256f4a44b041b9eb240b533
Type: security-commit

## Details
register ICA query server, fix panics in params query cli (#666)

Register the controller and host query servers to a chain.
Returns an error upon cli params query failure instead of panicing.

## Patch
### sei-ibc-go/modules/apps/27-interchain-accounts/controller/client/cli/query.go
```diff
@@ -26,7 +26,11 @@ func GetCmdParams() *cobra.Command {
 			}
 			queryClient := types.NewQueryClient(clientCtx)
 
-			res, _ := queryClient.Params(cmd.Context(), &types.QueryParamsRequest{})
+			res, err := queryClient.Params(cmd.Context(), &types.QueryParamsRequest{})
+			if err != nil {
+				return err
+			}
+
 			return clientCtx.PrintProto(res.Params)
 		},
 	}
```

### sei-ibc-go/modules/apps/27-interchain-accounts/host/client/cli/query.go
```diff
@@ -26,7 +26,11 @@ func GetCmdParams() *cobra.Command {
 			}
 			queryClient := types.NewQueryClient(clientCtx)
 
-			res, _ := queryClient.Params(cmd.Context(), &types.QueryParamsRequest{})
+			res, err := queryClient.Params(cmd.Context(), &types.QueryParamsRequest{})
+			if err != nil {
+				return err
+			}
+
 			return clientCtx.PrintProto(res.Params)
 		},
 	}
```

### sei-ibc-go/modules/apps/27-interchain-accounts/module.go
```diff
@@ -130,6 +130,8 @@ func (am AppModule) LegacyQuerierHandler(legacyQuerierCdc *codec.LegacyAmino) sd
 
 // RegisterServices registers module services
 func (am AppModule) RegisterServices(cfg module.Configurator) {
+	controllertypes.RegisterQueryServer(cfg.QueryServer(), am.controllerKeeper)
+	hosttypes.RegisterQueryServer(cfg.QueryServer(), am.hostKeeper)
 }
 
 // InitGenesis performs genesis initialization for the interchain accounts module.
```

### sei-ibc-go/modules/apps/transfer/client/cli/query.go
```diff
@@ -97,7 +97,11 @@ func GetCmdParams() *cobra.Command {
 			}
 			queryClient := types.NewQueryClient(clientCtx)
 
-			res, _ := queryClient.Params(cmd.Context(), &types.QueryParamsRequest{})
+			res, err := queryClient.Params(cmd.Context(), &types.QueryParamsRequest{})
+			if err != nil {
+				return err
+			}
+
 			return clientCtx.PrintProto(res.Params)
 		},
 	}
```
