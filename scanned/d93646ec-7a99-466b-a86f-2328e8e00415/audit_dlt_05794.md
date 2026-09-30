# [?] fix: attempt to fix panics for unresolvable imports by using GogoResolver (#7277)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2024-09-10
Source: https://github.com/cosmos/ibc-go/commit/79ddda541a51352bad0c4b64a96673f508187f63
Type: security-commit

## Details
fix: attempt to fix panics for unresolvable imports by using GogoResolver (#7277)

* fix: attempt to fix panics for unresolvable imports by using GogoResolver

* chore: add changelog

* chore: amend changelog

## Patch
### CHANGELOG.md
```diff
@@ -61,6 +61,8 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Bug Fixes
 
+* (apps/27-interchain-accounts) [\#7277](https://github.com/cosmos/ibc-go/pull/7277) Use `GogoResolver` when populating module query safe allow list to avoid panics from unresolvable protobuf dependencies.
+
 ## v9.0.0 (unreleased)
 
 ### Dependencies
```

### modules/apps/27-interchain-accounts/host/keeper/keeper.go
```diff
@@ -8,7 +8,6 @@ import (
 
 	gogoproto "github.com/cosmos/gogoproto/proto"
 	"google.golang.org/protobuf/proto"
-	"google.golang.org/protobuf/reflect/protodesc"
 	"google.golang.org/protobuf/reflect/protoreflect"
 
 	msgv1 "cosmossdk.io/api/cosmos/msg/v1"
@@ -276,21 +275,8 @@ func (k Keeper) SetParams(ctx context.Context, params types.Params) {
 
 // newModuleQuerySafeAllowList returns a list of all query paths labeled with module_query_safe in the proto files.
 func newModuleQuerySafeAllowList() []string {
-	fds, err := gogoproto.MergedGlobalFileDescriptors()
-	if err != nil {
-		panic(err)
-	}
-	// create the files using 'AllowUnresolvable' to avoid
-	// unnecessary panic: https://github.com/cosmos/ibc-go/issues/6435
-	protoFiles, err := protodesc.FileOptions{
-		AllowUnresolvable: true,
-	}.NewFiles(fds)
-	if err != nil {
-		panic(err)
-	}
-
 	allowList := []string{}
-	protoFiles.RangeFiles(func(fd protoreflect.FileDescriptor) bool {
+	gogoproto.GogoResolver.RangeFiles(func(fd protoreflect.FileDescriptor) bool {
 		for i := 0; i < fd.Services().Len(); i++ {
 			// Get the service descriptor
 			sd := fd.Services().Get(i)
```
