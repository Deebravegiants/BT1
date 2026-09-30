# [?] Fix panic metrics (#220)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2022-08-23
Source: https://github.com/sei-protocol/sei-chain/commit/35d35e158b6bebf4a85def6a0b7a61dca48998e4
Type: security-commit

## Details
Fix panic metrics (#220)

## Patch
### utils/panic.go
```diff
@@ -19,10 +19,11 @@ func PanicHandler(recoverCallback func(any)) func() {
 func MetricsPanicCallback(err any, ctx sdk.Context, key string) {
 	ctx.Logger().Error(fmt.Sprintf("panic %s occurred during order matching for: %s", err, key))
 	telemetry.IncrCounterWithLabels(
-		[]string{key},
+		[]string{"endblockpanic"},
 		1,
 		[]metrics.Label{
 			telemetry.NewLabel("error", fmt.Sprintf("%s", err)),
+			telemetry.NewLabel("module", key),
 		},
 	)
 }
```

### x/dex/module.go
```diff
@@ -220,10 +220,11 @@ func (am AppModule) BeginBlock(ctx sdk.Context, _ abci.RequestBeginBlock) {
 		if err := recover(); err != nil {
 			ctx.Logger().Error(fmt.Sprintf("panic occurred in %s BeginBlock: %s", types.ModuleName, err))
 			telemetry.IncrCounterWithLabels(
-				[]string{fmt.Sprintf("%s%s", types.ModuleName, "beginblockpanic")},
+				[]string{"beginblockpanic"},
 				1,
 				[]metrics.Label{
 					telemetry.NewLabel("error", fmt.Sprintf("%s", err)),
+					telemetry.NewLabel("module", types.ModuleName),
 				},
 			)
 		}
@@ -273,7 +274,7 @@ func (am AppModule) EndBlock(ctx sdk.Context, _ abci.RequestEndBlock) (ret []abc
 		if err := recover(); err != nil {
 			ctx.Logger().Error(fmt.Sprintf("panic occurred in %s EndBlock: %s", types.ModuleName, err))
 			telemetry.IncrCounterWithLabels(
-				[]string{("endblockpanic")},
+				[]string{"endblockpanic"},
 				1,
 				[]metrics.Label{
 					telemetry.NewLabel("error", fmt.Sprintf("%s", err)),
```

### x/epoch/module.go
```diff
@@ -177,10 +177,11 @@ func (am AppModule) BeginBlock(ctx sdk.Context, _ abci.RequestBeginBlock) {
 		if err := recover(); err != nil {
 			ctx.Logger().Error(fmt.Sprintf("panic occurred in %s BeginBlock: %s", types.ModuleName, err))
 			telemetry.IncrCounterWithLabels(
-				[]string{fmt.Sprintf("%s%s", types.ModuleName, "beginblockpanic")},
+				[]string{"beginblockpanic"},
 				1,
 				[]metrics.Label{
 					telemetry.NewLabel("error", fmt.Sprintf("%s", err)),
+					telemetry.NewLabel("module", types.ModuleName),
 				},
 			)
 		}
```

### x/mint/module.go
```diff
@@ -155,10 +155,11 @@ func (am AppModule) BeginBlock(ctx sdk.Context, _ abci.RequestBeginBlock) {
 		if err := recover(); err != nil {
 			ctx.Logger().Error(fmt.Sprintf("panic occurred in %s BeginBlock: %s", types.ModuleName, err))
 			telemetry.IncrCounterWithLabels(
-				[]string{fmt.Sprintf("%s%s", types.ModuleName, "beginblockpanic")},
+				[]string{"beginblockpanic"},
 				1,
 				[]metrics.Label{
 					telemetry.NewLabel("error", fmt.Sprintf("%s", err)),
+					telemetry.NewLabel("module", types.ModuleName),
 				},
 			)
 		}
```

### x/oracle/module.go
```diff
@@ -176,10 +176,11 @@ func (am AppModule) EndBlock(ctx sdk.Context, _ abci.RequestEndBlock) (ret []abc
 		if err := recover(); err != nil {
 			ctx.Logger().Error(fmt.Sprintf("panic occurred in %s EndBlock: %s", types.ModuleName, err))
 			telemetry.IncrCounterWithLabels(
-				[]string{fmt.Sprintf("%s%s", types.ModuleName, "endblockpanic")},
+				[]string{"endblockpanic"},
 				1,
 				[]metrics.Label{
 					telemetry.NewLabel("error", fmt.Sprintf("%s", err)),
+					telemetry.NewLabel("module", types.ModuleName),
 				},
 			)
 			ret = []abci.ValidatorUpdate{}
```
