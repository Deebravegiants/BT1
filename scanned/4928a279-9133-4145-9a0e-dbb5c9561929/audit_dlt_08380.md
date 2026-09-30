# [?] fix(codec,x/tx): lower nested Any depth cap from 10000 to 64 to reduce DoS amplification (#26587)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2026-07-27
Source: https://github.com/cosmos/cosmos-sdk/commit/6e84a47bb09facbb5e4d9a8a5c6822c3ef77a42e
Type: security-commit

## Details
fix(codec,x/tx): lower nested Any depth cap from 10000 to 64 to reduce DoS amplification (#26587)

Co-authored-by: Dmitry S <11892559+swift1337@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -80,6 +80,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Bug Fixes
 
+* (codec) [#26587](https://github.com/cosmos/cosmos-sdk/pull/26587) Lower the nested `google.protobuf.Any` recursion depth cap in unknown-field validation from 10,000 to 64, reducing CPU-amplification DoS risk from deeply nested `Any` wrappers. No legitimate message nests `Any` anywhere near that deep.
 * (x/feegrant) [#26596](https://github.com/cosmos/cosmos-sdk/pull/26596) Honor the `PageRequest` offset and `count_total` in the `Allowances` and `AllowancesByGranter` gRPC queries, which previously collected grants inside the pagination predicate and so returned offset-skipped and beyond-limit results.
 * (x/authz) [#26588](https://github.com/cosmos/cosmos-sdk/pull/26588) Cap the number of expired grants pruned per `BeginBlocker` call to 200, matching `x/feegrant`'s existing pattern, so a block where many grants expire at once can't cause unbounded work.
 * (client) [#26524](https://github.com/cosmos/cosmos-sdk/pull/26524) Fix file handle leak in the `snapshot dump` command where chunk files were deferred-closed inside the loop, keeping every chunk's handle open until the command returned (follow-up to #25811).
```

### codec/unknownproto/unknown_fields.go
```diff
@@ -21,6 +21,9 @@ import (
 
 const bit11NonCritical = 1 << 10
 
+// maxAnyNestingDepth caps recursion cost from chained Any redirections; 64 exceeds any legitimate nesting.
+const maxAnyNestingDepth = 64
+
 type descriptorIface interface {
 	Descriptor() ([]byte, []int)
 }
@@ -40,8 +43,7 @@ func RejectUnknownFieldsStrict(bz []byte, msg proto.Message, resolver jsonpb.Any
 // This function traverses inside of messages nested via google.protobuf.Any. It does not do any deserialization of the proto.Message.
 // An AnyResolver must be provided for traversing inside google.protobuf.Any's.
 func RejectUnknownFields(bz []byte, msg proto.Message, allowUnknownNonCriticals bool, resolver jsonpb.AnyResolver) (hasUnknownNonCriticals bool, err error) {
-	// recursion limit with same default as https://github.com/protocolbuffers/protobuf-go/blob/v1.35.2/encoding/protowire/wire.go#L28
-	return doRejectUnknownFields(bz, msg, allowUnknownNonCriticals, resolver, 10_000)
+	return doRejectUnknownFields(bz, msg, allowUnknownNonCriticals, resolver, maxAnyNestingDepth)
 }
 
 func doRejectUnknownFields(
```

### x/tx/decode/unknown.go
```diff
@@ -14,6 +14,9 @@ import (
 
 const bit11NonCritical = 1 << 10
 
+// maxAnyNestingDepth caps recursion cost from chained Any redirections; 64 exceeds any legitimate nesting.
+const maxAnyNestingDepth = 64
+
 var (
 	anyDesc     = (&anypb.Any{}).ProtoReflect().Descriptor()
 	anyFullName = anyDesc.FullName()
@@ -33,8 +36,7 @@ func RejectUnknownFieldsStrict(bz []byte, msg protoreflect.MessageDescriptor, re
 // This function traverses inside of messages nested via google.protobuf.Any. It does not do any deserialization of the proto.Message.
 // An AnyResolver must be provided for traversing inside google.protobuf.Any's.
 func RejectUnknownFields(bz []byte, desc protoreflect.MessageDescriptor, allowUnknownNonCriticals bool, resolver protodesc.Resolver) (hasUnknownNonCriticals bool, err error) {
-	// recursion limit with same default as https://github.com/protocolbuffers/protobuf-go/blob/v1.35.2/encoding/protowire/wire.go#L28
-	return doRejectUnknownFields(bz, desc, allowUnknownNonCriticals, resolver, 10_000)
+	return doRejectUnknownFields(bz, desc, allowUnknownNonCriticals, resolver, maxAnyNestingDepth)
 }
 
 func doRejectUnknownFields(
```
