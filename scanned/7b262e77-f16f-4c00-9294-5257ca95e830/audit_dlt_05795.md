# [?] fix(ica-host): refactor newModuleQuerySafeAllowList to avoid panic (#6436)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2024-06-06
Source: https://github.com/cosmos/ibc-go/commit/a16c549b5ac982461c5c3c53887deef256474d37
Type: security-commit

## Details
fix(ica-host): refactor newModuleQuerySafeAllowList to avoid panic (#6436)

* fix(ica-host): refactor newModuleQuerySafeAllowList to avoid panic due to AllowUnresolvable field

* add changelog entry

* Apply suggestions from code review

Co-authored-by: colin axnér <25233464+colin-axner@users.noreply.github.com>

---------

Co-authored-by: Carlos Rodriguez <carlos@interchain.io>
Co-authored-by: DimitrisJim <d.f.hilliard@gmail.com>
Co-authored-by: colin axnér <25233464+colin-axner@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -67,6 +67,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 * (apps/27-interchain-accounts) [\#5533](https://github.com/cosmos/ibc-go/pull/5533) ICA host sets the host connection ID on `OnChanOpenTry`, so that ICA controller implementations are not obliged to set the value on `OnChanOpenInit` if they are not able.
 * (core/02-client, core/03-connection, apps/27-interchain-accounts) [\#6256](https://github.com/cosmos/ibc-go/pull/6256) Add length checking of array fields in messages.
+* (apps/27-interchain-accounts) [\#6436](https://github.com/cosmos/ibc-go/pull/6436) Refactor ICA host keeper instantiation method to avoid panic related to proto files.
 
 ### Features
 
```

### modules/apps/27-interchain-accounts/host/keeper/keeper.go
```diff
@@ -7,6 +7,7 @@ import (
 
 	gogoproto "github.com/cosmos/gogoproto/proto"
 	"google.golang.org/protobuf/proto"
+	"google.golang.org/protobuf/reflect/protodesc"
 	"google.golang.org/protobuf/reflect/protoreflect"
 
 	msgv1 "cosmossdk.io/api/cosmos/msg/v1"
@@ -276,7 +277,15 @@ func (k Keeper) SetParams(ctx sdk.Context, params types.Params) {
 
 // newModuleQuerySafeAllowList returns a list of all query paths labeled with module_query_safe in the proto files.
 func newModuleQuerySafeAllowList() []string {
-	protoFiles, err := gogoproto.MergedRegistry()
+	fds, err := gogoproto.MergedGlobalFileDescriptors()
+	if err != nil {
+		panic(err)
+	}
+	// create the files using 'AllowUnresolvable' to avoid
+	// unnecessary panic: https://github.com/cosmos/ibc-go/issues/6435
+	protoFiles, err := protodesc.FileOptions{
+		AllowUnresolvable: true,
+	}.NewFiles(fds)
 	if err != nil {
 		panic(err)
 	}
```
