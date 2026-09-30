# [?] Fix panic on closing nil db  (#3175)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-11-03
Source: https://github.com/algorand/go-algorand/commit/009b7981e1245180ccae5be93674e643157aad26
Type: security-commit

## Details
Fix panic on closing nil db  (#3175)

## Summary

FillDBWithParticipationKeys will return empty PersistedParticipation when lastValid is less than firstValid.
When this happens, newPart will not have partdb in newPart.Store, instead, will have an empty object.
Calling Close on the empty object will call close on nil Accessor pointer and panic.

This change avoids using the returned object with non-nil error, and properly closes the db with the valid object.
## Test Plan

Added test to verify the proper handling of the different errors returned from FillDBWithParticipationKeys and handled by GenParticipationKeysTo.

## Patch
### data/account/participation.go
```diff
@@ -164,7 +164,7 @@ func (part PersistedParticipation) PersistNewParent() error {
 // FillDBWithParticipationKeys initializes the passed database with participation keys
 func FillDBWithParticipationKeys(store db.Accessor, address basics.Address, firstValid, lastValid basics.Round, keyDilution uint64) (part PersistedParticipation, err error) {
 	if lastValid < firstValid {
-		err = fmt.Errorf("FillDBWithParticipationKeys: lastValid %d is after firstValid %d", lastValid, firstValid)
+		err = fmt.Errorf("FillDBWithParticipationKeys: firstValid %d is after lastValid %d", firstValid, lastValid)
 		return
 	}
 
```

### libgoal/participation.go
```diff
@@ -166,7 +166,7 @@ func (c *Client) GenParticipationKeysTo(address string, firstValid, lastValid, k
 	// Fill the database with new participation keys
 	newPart, err := account.FillDBWithParticipationKeys(partdb, parsedAddr, firstRound, lastRound, keyDilution)
 	part = newPart.Participation
-	newPart.Close()
+	partdb.Close()
 	return part, partKeyPath, err
 }
 
```

### node/node_test.go
```diff
@@ -129,10 +129,10 @@ func setupFullNodes(t *testing.T, proto protocol.ConsensusVersion, verificationP
 			panic(err)
 		}
 		part, err := account.FillDBWithParticipationKeys(access, root.Address(), firstRound, lastRound, config.Consensus[protocol.ConsensusCurrentVersion].DefaultKeyDilution)
-		access.Close()
 		if err != nil {
 			panic(err)
 		}
+		access.Close()
 
 		data := basics.AccountData{
 			Status:      basics.Online,
```

### test/e2e-go/features/transactions/onlineStatusChange_test.go
```diff
@@ -17,6 +17,7 @@
 package transactions
 
 import (
+	"fmt"
 	"path/filepath"
 	"testing"
 
@@ -145,3 +146,36 @@ func testAccountsCanChangeOnlineState(t *testing.T, templatePath string) {
 		a.Equal(unmarkedAccountStatus.Status, basics.NotParticipating.String())
 	}
 }
+
+func TestCloseOnError(t *testing.T) {
+	partitiontest.PartitionTest(t)
+
+	t.Parallel()
+	a := require.New(fixtures.SynchronizedTest(t))
+
+	var fixture fixtures.RestClientFixture
+	fixture.Setup(t, filepath.Join("nettemplates", "TwoNodesPartlyOfflineVFuture.json"))
+	defer fixture.Shutdown()
+	client := fixture.LibGoalClient
+
+	// Capture the account we're tracking
+	accountList, err := fixture.GetWalletsSortedByBalance()
+	a.NoError(err)
+
+	initiallyOnline := accountList[0].Address  // 35% stake
+	initiallyOffline := accountList[1].Address // 20% stake
+
+	// get the current round for partkey creation
+	_, curRound := fixture.GetBalanceAndRound(initiallyOnline)
+
+	// make a participation key for initiallyOffline
+	_, _, err = client.GenParticipationKeys(initiallyOffline, 0, curRound+1000, 0)
+	a.NoError(err)
+	// check duplicate keys does not crash
+	_, _, err = client.GenParticipationKeys(initiallyOffline, 0, curRound+1000, 0)
+	a.Equal("PersistedParticipation.Persist: failed to install database: table ParticipationAccount already exists", err.Error())
+	// check lastValid < firstValid does not crash
+	_, _, err = client.GenParticipationKeys(initiallyOffline, curRound+1001, curRound+1000, 0)
+	expected := fmt.Sprintf("FillDBWithParticipationKeys: firstValid %d is after lastValid %d", int(curRound+1001), int(curRound+1000))
+	a.Equal(expected, err.Error())
+}
```
