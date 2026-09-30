# [?] Fix nil dereference in etcdraft config parsing

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-02-24
Source: https://github.com/hyperledger/fabric/commit/046253c8b8fb0c4b86aa0ee104b35f3930d1455c
Type: security-commit

## Details
Fix nil dereference in etcdraft config parsing

The etcdraft config parsing code currently checks that the consensus
metadata is not nil, but it fails to check that the options are not nil.
This commit simply adds the additional check and backfills some testing
around this validation function.

Signed-off-by: Jason Yellick <jyellick@us.ibm.com>

## Patch
### orderer/consensus/etcdraft/util.go
```diff
@@ -204,6 +204,10 @@ func CheckConfigMetadata(metadata *etcdraft.ConfigMetadata) error {
 		return errors.Errorf("nil Raft config metadata")
 	}
 
+	if metadata.Options == nil {
+		return errors.Errorf("nil Raft config metadata options")
+	}
+
 	if metadata.Options.HeartbeatTick == 0 ||
 		metadata.Options.ElectionTick == 0 ||
 		metadata.Options.MaxInflightBlocks == 0 {
@@ -215,7 +219,7 @@ func CheckConfigMetadata(metadata *etcdraft.ConfigMetadata) error {
 	// check Raft options
 	if metadata.Options.ElectionTick <= metadata.Options.HeartbeatTick {
 		return errors.Errorf("ElectionTick (%d) must be greater than HeartbeatTick (%d)",
-			metadata.Options.HeartbeatTick, metadata.Options.HeartbeatTick)
+			metadata.Options.ElectionTick, metadata.Options.HeartbeatTick)
 	}
 
 	if d, err := time.ParseDuration(metadata.Options.TickInterval); err != nil {
```

### orderer/consensus/etcdraft/util_test.go
```diff
@@ -152,6 +152,11 @@ func TestCheckConfigMetadata(t *testing.T) {
 			metadata:    nil,
 			errRegex:    "nil Raft config metadata",
 		},
+		{
+			description: "nil options",
+			metadata:    &etcdraftproto.ConfigMetadata{},
+			errRegex:    "nil Raft config metadata options",
+		},
 		{
 			description: "HeartbeatTick is 0",
 			metadata: &etcdraftproto.ConfigMetadata{
```
