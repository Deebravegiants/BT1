# [?] Fix data race in TestBlockingEnqueue (#850)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-03-12
Source: https://github.com/hyperledger/fabric/commit/db2e930a348b5eb8ab1dd40bf813f5dc80acc854
Type: security-commit

## Details
Fix data race in TestBlockingEnqueue (#850)

In some tests we need to overwrite the mocks.Mock field
of the mock, however it could be that it is used concurrently
by other goroutines.

We use a lock to ensure mutual exclusion and memory cohesion,
and the mock methods lock before calling the mocked method.

The lock was only used upon demand and not consistently.

I made the lock to be always activated.

Change-Id: Iffd02f681b144d2456640922c4c5a6438109a40e
Signed-off-by: yacovm <yacovm@il.ibm.com>

## Patch
### gossip/state/state_test.go
```diff
@@ -209,7 +209,11 @@ func (mc *mockCommitter) CommitLegacy(blockAndPvtData *ledger.BlockAndPvtData, c
 }
 
 func (mc *mockCommitter) GetPvtDataAndBlockByNum(seqNum uint64) (*ledger.BlockAndPvtData, error) {
-	args := mc.Called(seqNum)
+	mc.Lock()
+	m := mc.Mock
+	mc.Unlock()
+
+	args := m.Called(seqNum)
 	return args.Get(0).(*ledger.BlockAndPvtData), args.Error(1)
 }
 
@@ -225,15 +229,22 @@ func (mc *mockCommitter) LedgerHeight() (uint64, error) {
 }
 
 func (mc *mockCommitter) DoesPvtDataInfoExistInLedger(blkNum uint64) (bool, error) {
-	args := mc.Called(blkNum)
+	mc.Lock()
+	m := mc.Mock
+	mc.Unlock()
+	args := m.Called(blkNum)
 	return args.Get(0).(bool), args.Error(1)
 }
 
 func (mc *mockCommitter) GetBlocks(blockSeqs []uint64) []*pcomm.Block {
-	if mc.Called(blockSeqs).Get(0) == nil {
+	mc.Lock()
+	m := mc.Mock
+	mc.Unlock()
+
+	if m.Called(blockSeqs).Get(0) == nil {
 		return nil
 	}
-	return mc.Called(blockSeqs).Get(0).([]*pcomm.Block)
+	return m.Called(blockSeqs).Get(0).([]*pcomm.Block)
 }
 
 func (*mockCommitter) GetMissingPvtDataTracker() (ledger.MissingPvtDataTracker, error) {
```
