# [?] adding lock to fix data race between file and api (#17439)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-09-01
Source: https://github.com/OffchainLabs/prysm/commit/402fdb1b25270037fd9ab8547841a3564770c430
Type: security-commit

## Details
adding lock to fix data race between file and api (#17439)

**What type of PR is this?**

 Bug fix

**What does this PR do? Why is it needed?**

old bug that is difficult to trigger, fixes race between keymanager api
and file changes

**Which issue(s) does this PR fix?**

Fixes #

**Other notes for review**

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [ ] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

## Patch
### changelog/james-prysm_local-keymanager-store-lock.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Serialize local keymanager account store mutations to fix a data race between keystore file reloads and keymanager API imports/deletions.
```

### validator/keymanager/local/BUILD.bazel
```diff
@@ -62,6 +62,7 @@ go_test(
         "//proto/prysm/v1alpha1/validator-client:go_default_library",
         "//testing/assert:go_default_library",
         "//testing/require:go_default_library",
+        "//validator/accounts/iface:go_default_library",
         "//validator/accounts/testing:go_default_library",
         "//validator/keymanager:go_default_library",
         "@com_github_ethereum_go_ethereum//common/hexutil:go_default_library",
```

### validator/keymanager/local/delete.go
```diff
@@ -21,6 +21,8 @@ import (
 func (km *Keymanager) DeleteKeystores(
 	ctx context.Context, publicKeys [][]byte,
 ) ([]*keymanager.KeyStatus, error) {
+	km.mu.Lock()
+	defer km.mu.Unlock()
 	// Check for duplicate keys and filter them out.
 	trackedPublicKeys := make(map[[fieldparams.BLSPubkeyLength]byte]bool)
 	statuses := make([]*keymanager.KeyStatus, 0, len(publicKeys))
@@ -64,7 +66,7 @@ func (km *Keymanager) DeleteKeystores(
 		return statuses, nil
 	}
 	// 3 & 4) save to disk and re-initializes keystore
-	if err := km.SaveStoreAndReInitialize(ctx, storeCopy); err != nil {
+	if err := km.saveStoreAndReInitialize(ctx, storeCopy); err != nil {
 		return nil, err
 	}
 
```

### validator/keymanager/local/import.go
```diff
@@ -32,6 +32,8 @@ func (km *Keymanager) ImportKeystores(
 	if len(passwords) != len(keystores) {
 		return nil, ErrMismatchedNumPasswords
 	}
+	km.mu.Lock()
+	defer km.mu.Unlock()
 	decryptor := keystorev4.New()
 	bar := initializeProgressBar(len(keystores), "Importing accounts...")
 	keys := map[string]string{}
@@ -86,7 +88,7 @@ func (km *Keymanager) ImportKeystores(
 		storeCopy.PrivateKeys = append(storeCopy.PrivateKeys, []byte(privKey))
 	}
 	// 3) & 4) save to disk and re-initializes keystore
-	if err := km.SaveStoreAndReInitialize(ctx, storeCopy); err != nil {
+	if err := km.saveStoreAndReInitialize(ctx, storeCopy); err != nil {
 		return nil, err
 	}
 
@@ -105,14 +107,16 @@ func (km *Keymanager) ImportKeypairs(ctx context.Context, privKeys, pubKeys [][]
 			"number of private keys and public keys is not equal: %d != %d", len(privKeys), len(pubKeys),
 		)
 	}
+	km.mu.Lock()
+	defer km.mu.Unlock()
 	// 1) Copy the in memory keystore
 	storeCopy := km.accountsStore.Copy()
 
 	// 2) Update store and remove duplicates
 	updateAccountsStoreKeys(storeCopy, privKeys, pubKeys)
 
 	// 3) & 4) save to disk and re-initializes keystore
-	if err := km.SaveStoreAndReInitialize(ctx, storeCopy); err != nil {
+	if err := km.saveStoreAndReInitialize(ctx, storeCopy); err != nil {
 		return err
 	}
 
```

### validator/keymanager/local/import_test.go
```diff
@@ -1,14 +1,20 @@
 package local
 
 import (
+	"context"
+	"errors"
 	"fmt"
+	"os"
+	"path/filepath"
 	"strconv"
 	"testing"
+	"time"
 
 	"github.com/OffchainLabs/prysm/v7/crypto/bls"
 	"github.com/OffchainLabs/prysm/v7/encoding/bytesutil"
 	"github.com/OffchainLabs/prysm/v7/testing/assert"
 	"github.com/OffchainLabs/prysm/v7/testing/require"
+	accountsiface "github.com/OffchainLabs/prysm/v7/validator/accounts/iface"
 	mock "github.com/OffchainLabs/prysm/v7/validator/accounts/testing"
 	"github.com/OffchainLabs/prysm/v7/validator/keymanager"
 	"github.com/ethereum/go-ethereum/common/hexutil"
@@ -260,3 +266,90 @@ func TestLocalKeymanager_ImportKeystores(t *testing.T) {
 		require.DeepEqual(t, dr.accountsStore, copyStore)
 	})
 }
+
+// fsWallet is a minimal wallet backed by real files so the keystore file watcher runs.
+type fsWallet struct {
+	dir      string
+	password string
+}
+
+func (w *fsWallet) AccountsDir() string { return w.dir }
+func (w *fsWallet) Dir() string         { return w.dir }
+func (w *fsWallet) Password() string    { return w.password }
+
+func (w *fsWallet) ReadFileAtPath(_ context.Context, pathName, fileName string) ([]byte, error) {
+	b, err := os.ReadFile(filepath.Join(w.dir, pathName, fileName))
+	if os.IsNotExist(err) {
+		return nil, errors.New("no files found")
+	}
+	return b, err
+}
+
+func (w *fsWallet) WriteFileAtPath(_ context.Context, pathName, fileName string, data []byte) (bool, error) {
+	fp := filepath.Join(w.dir, pathName, fileName)
+	if err := os.MkdirAll(filepath.Dir(fp), 0700); err != nil {
+		return false, err
+	}
+	_, statErr := os.Stat(fp)
+	if err := os.WriteFile(fp, data, 0600); err != nil {
+		return false, err
+	}
+	return statErr == nil, nil
+}
+
+func (*fsWallet) InitializeKeymanager(context.Context, accountsiface.InitKeymanagerConfig) (keymanager.IKeymanager, error) {
+	return nil, nil
+}
+
+func (*fsWallet) KeymanagerKind() keymanager.Kind { return keymanager.Local }
+
+func TestLocalKeymanager_ImportKeypairs(t *testing.T) {
+	t.Run("sequential imports with active file watcher", func(t *testing.T) {
+		ResetCaches()
+		ctx, cancel := context.WithCancel(t.Context())
+		defer cancel()
+		km, err := NewKeymanager(ctx, &SetupConfig{Wallet: &fsWallet{dir: t.TempDir(), password: password}})
+		require.NoError(t, err)
+
+		// Each import rewrites the keystore file, which the watcher reloads concurrently.
+		numKeys := 5
+		for range numKeys {
+			priv, err := bls.RandKey()
+			require.NoError(t, err)
+			require.NoError(t, km.ImportKeypairs(ctx, [][]byte{priv.Marshal()}, [][]byte{priv.PublicKey().Marshal()}))
+			time.Sleep(10 * time.Millisecond)
+		}
+		keys, err := km.FetchValidatingPublicKeys(ctx)
+		require.NoError(t, err)
+		require.Equal(t, numKeys, len(keys))
+	})
+	t.Run("imports race concurrent keystore file reloads", func(t *testing.T) {
+		ResetCaches()
+		ctx := t.Context()
+		w := &fsWallet{dir: t.TempDir(), password: password}
+		km, err := NewKeymanager(ctx, &SetupConfig{Wallet: w})
+		require.NoError(t, err)
+		seed, err := bls.RandKey()
+		require.NoError(t, err)
+		require.NoError(t, km.ImportKeypairs(ctx, [][]byte{seed.Marshal()}, [][]byte{seed.PublicKey().Marshal()}))
+
+		accountsFile := filepath.Join(w.dir, AccountsPath, AccountsKeystoreFileName)
+		done := make(chan struct{})
+		go func() {
+			defer close(done)
+			for range 3 {
+				km.reloadAccountsFromKeystoreFile(accountsFile)
+			}
+		}()
+		for range 3 {
+			priv, err := bls.RandKey()
+			require.NoError(t, err)
+			require.NoError(t, km.ImportKeypairs(ctx, [][]byte{priv.Marshal()}, [][]byte{priv.PublicKey().Marshal()}))
+		}
+		<-done
+
+		keys, err := km.FetchValidatingPublicKeys(ctx)
+		require.NoError(t, err)
+		require.Equal(t, 4, len(keys))
+	})
+}
```

### validator/keymanager/local/keymanager.go
```diff
@@ -41,6 +41,7 @@ const (
 // Keymanager implementation for local keystores utilizing EIP-2335.
 type Keymanager struct {
 	wallet              iface.Wallet
+	mu                  sync.Mutex // serializes accountsStore mutations
 	accountsStore       *accountStore
 	accountsChangedFeed *event.Feed
 }
@@ -233,14 +234,22 @@ func (km *Keymanager) initializeAccountKeystore(ctx context.Context) error {
 
 // CreateAccountsKeystore creates a new keystore holding the provided keys.
 func (km *Keymanager) CreateAccountsKeystore(ctx context.Context, privateKeys [][]byte, publicKeys [][]byte) (*AccountsKeystoreRepresentation, error) {
-	if err := km.CreateOrUpdateInMemoryAccountsStore(ctx, privateKeys, publicKeys); err != nil {
+	km.mu.Lock()
+	defer km.mu.Unlock()
+	if err := km.createOrUpdateInMemoryAccountsStore(ctx, privateKeys, publicKeys); err != nil {
 		return nil, err
 	}
 	return CreateAccountsKeystoreRepresentation(ctx, km.accountsStore, km.wallet.Password())
 }
 
 // SaveStoreAndReInitialize saves the store to disk and re-initializes the account keystore from file
 func (km *Keymanager) SaveStoreAndReInitialize(ctx context.Context, store *accountStore) error {
+	km.mu.Lock()
+	defer km.mu.Unlock()
+	return km.saveStoreAndReInitialize(ctx, store)
+}
+
+func (km *Keymanager) saveStoreAndReInitialize(ctx context.Context, store *accountStore) error {
 	// Save the copy to disk
 	accountsKeystore, err := CreateAccountsKeystoreRepresentation(ctx, store, km.wallet.Password())
 	if err != nil {
@@ -269,7 +278,7 @@ func (km *Keymanager) SaveStoreAndReInitialize(ctx context.Context, store *accou
 	}
 
 	// manually reload the account from the keystore the first time
-	km.reloadAccountsFromKeystoreFile(filepath.Join(km.wallet.AccountsDir(), AccountsPath, AccountsKeystoreFileName))
+	km.reloadAccountsFromKeystoreFileLocked(filepath.Join(km.wallet.AccountsDir(), AccountsPath, AccountsKeystoreFileName))
 	// listen to account changes of the new file
 	go km.listenForAccountChanges(ctx)
 	return nil
@@ -311,7 +320,13 @@ func CreateEmptyKeyStoreRepresentationForNewWallet(ctx context.Context, walletPa
 
 // CreateOrUpdateInMemoryAccountsStore will set or update the local accounts store and update the local cache.
 // This function DOES NOT save the accounts store to disk.
-func (km *Keymanager) CreateOrUpdateInMemoryAccountsStore(_ context.Context, privateKeys, publicKeys [][]byte) error {
+func (km *Keymanager) CreateOrUpdateInMemoryAccountsStore(ctx context.Context, privateKeys, publicKeys [][]byte) error {
+	km.mu.Lock()
+	defer km.mu.Unlock()
+	return km.createOrUpdateInMemoryAccountsStore(ctx, privateKeys, publicKeys)
+}
+
+func (km *Keymanager) createOrUpdateInMemoryAccountsStore(_ context.Context, privateKeys, publicKeys [][]byte) error {
 	if len(privateKeys) != len(publicKeys) {
 		return fmt.Errorf(
 			"number of private keys and public keys is not equal: %d != %d", len(privateKeys), len(publicKeys),
```

### validator/keymanager/local/refresh.go
```diff
@@ -82,6 +82,13 @@ func (km *Keymanager) listenForAccountChanges(ctx context.Context) {
 }
 
 func (km *Keymanager) reloadAccountsFromKeystoreFile(accountsFilePath string) {
+	km.mu.Lock()
+	defer km.mu.Unlock()
+	km.reloadAccountsFromKeystoreFileLocked(accountsFilePath)
+}
+
+// reloadAccountsFromKeystoreFileLocked requires km.mu to be held.
+func (km *Keymanager) reloadAccountsFromKeystoreFileLocked(accountsFilePath string) {
 	if km.wallet == nil {
 		log.Error("Could not reload accounts because wallet was undefined")
 		return
```
