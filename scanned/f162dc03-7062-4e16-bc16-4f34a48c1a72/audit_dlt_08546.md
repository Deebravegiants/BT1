# [?] Algod: fix nil deref while fetching stateproof secrets (#4554)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2022-09-19
Source: https://github.com/algorand/go-algorand/commit/0b1c9f32f87810371998663868faf641cb1ef6db
Type: security-commit

## Details
Algod: fix nil deref while fetching stateproof secrets (#4554)

## Patch
### data/account/participationRegistry.go
```diff
@@ -220,6 +220,9 @@ var ErrNoKeyForID = errors.New("no valid key found for the participationID")
 // ErrSecretNotFound is used when attempting to lookup secrets for a particular round.
 var ErrSecretNotFound = errors.New("the participation ID did not have secrets for the requested round")
 
+// ErrStateProofVerifierNotFound states that no state proof field was found.
+var ErrStateProofVerifierNotFound = errors.New("record contains no StateProofVerifier")
+
 // ParticipationRegistry contain all functions for interacting with the Participation Registry.
 type ParticipationRegistry interface {
 	// Insert adds a record to storage and computes the ParticipationID
@@ -767,6 +770,10 @@ func (db *participationDB) GetStateProofSecretsForRound(id ParticipationID, roun
 	if err != nil {
 		return StateProofSecretsForRound{}, err
 	}
+	if partRecord.StateProof == nil {
+		return StateProofSecretsForRound{},
+			fmt.Errorf("%w: for participation ID %v", ErrStateProofVerifierNotFound, id)
+	}
 
 	var result StateProofSecretsForRound
 	result.ParticipationRecord = partRecord.ParticipationRecord
```

### data/account/participationRegistry_test.go
```diff
@@ -27,10 +27,9 @@ import (
 	"os"
 	"path/filepath"
 	"strconv"
-	"sync/atomic"
-
 	"strings"
 	"sync"
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -958,6 +957,36 @@ func TestAddStateProofKeys(t *testing.T) {
 	}
 }
 
+func TestGetRoundSecretsWithNilStateProofVerifier(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	a := assert.New(t)
+	registry, dbfile := getRegistry(t)
+	defer registryCloseTest(t, registry, dbfile)
+
+	access, err := db.MakeAccessor("stateprooftest", false, true)
+	if err != nil {
+		panic(err)
+	}
+	root, err := GenerateRoot(access)
+	p, err := FillDBWithParticipationKeys(access, root.Address(), 0, basics.Round(stateProofIntervalForTests*2), 3)
+	access.Close()
+	a.NoError(err)
+
+	// Install a key for testing
+	id, err := registry.Insert(p.Participation)
+	a.NoError(err)
+
+	// ensuring that GetStateProof will receive from cache a participationRecord without StateProof field.
+	prt := registry.cache[id]
+	prt.StateProof = nil
+	registry.cache[id] = prt
+
+	a.NoError(registry.Flush(defaultTimeout))
+
+	_, err = registry.GetStateProofSecretsForRound(id, basics.Round(stateProofIntervalForTests)-1)
+	a.ErrorIs(err, ErrStateProofVerifierNotFound)
+}
+
 func TestSecretNotFound(t *testing.T) {
 	partitiontest.PartitionTest(t)
 	a := require.New(t)
```

### data/accountManager.go
```diff
@@ -79,10 +79,10 @@ func (manager *AccountManager) Keys(rnd basics.Round) (out []account.Participati
 // StateProofKeys returns a list of Participation accounts, and their stateproof secrets
 func (manager *AccountManager) StateProofKeys(rnd basics.Round) (out []account.StateProofSecretsForRound) {
 	for _, part := range manager.registry.GetAll() {
-		if part.OverlapsInterval(rnd, rnd) {
+		if part.StateProof != nil && part.OverlapsInterval(rnd, rnd) {
 			partRndSecrets, err := manager.registry.GetStateProofSecretsForRound(part.ParticipationID, rnd)
 			if err != nil {
-				manager.log.Errorf("error while loading round secrets from participation registry: %w", err)
+				manager.log.Errorf("error while loading round secrets from participation registry: %v", err)
 				continue
 			}
 			out = append(out, partRndSecrets)
```

### data/accountManager_test.go
```diff
@@ -17,6 +17,7 @@
 package data
 
 import (
+	"bytes"
 	"fmt"
 	"os"
 	"path/filepath"
@@ -248,3 +249,46 @@ func TestAccountManagerOverlappingStateProofKeys(t *testing.T) {
 	res = acctManager.StateProofKeys(basics.Round(merklesignature.KeyLifetimeDefault * 3))
 	a.Equal(1, len(res))
 }
+
+func TestGetStateProofKeysDontLogErrorOnNilStateProof(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	a := assert.New(t)
+
+	registry, dbName := getRegistryImpl(t, false, true)
+	defer registryCloseTest(t, registry, dbName)
+
+	log := logging.TestingLog(t)
+	log.SetLevel(logging.Error)
+	logbuffer := bytes.NewBuffer(nil)
+	log.SetOutput(logbuffer)
+
+	acctManager := MakeAccountManager(log, registry)
+	databaseFiles := make([]string, 0)
+	defer func() {
+		for _, fileName := range databaseFiles {
+			os.Remove(fileName)
+			os.Remove(fileName + "-shm")
+			os.Remove(fileName + "-wal")
+			os.Remove(fileName + "-journal")
+		}
+	}()
+
+	// Generate 2 participations under the same account
+	store, err := db.MakeAccessor("stateprooftest", false, true)
+	a.NoError(err)
+	root, err := account.GenerateRoot(store)
+	a.NoError(err)
+	part1, err := account.FillDBWithParticipationKeys(store, root.Address(), 0, basics.Round(merklesignature.KeyLifetimeDefault*2), 3)
+	a.NoError(err)
+	store.Close()
+
+	part1.StateProofSecrets = nil
+	_, err = registry.Insert(part1.Participation)
+	a.NoError(err)
+
+	logbuffer.Reset()
+	acctManager.StateProofKeys(1)
+	lg := logbuffer.String()
+	a.False(strings.Contains(lg, account.ErrStateProofVerifierNotFound.Error()))
+	a.False(strings.Contains(lg, "level=error"), "expected no error in log:", lg)
+}
```
