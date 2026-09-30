# [?] cmd, miner, signer: avoid panic if keystore is not available (#27039)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-04-03
Source: https://github.com/ethereum/go-ethereum/commit/94457cce072d1e45f47d13dce290e0473615ec5d
Type: security-commit

## Details
cmd, miner, signer: avoid panic if keystore is not available (#27039)

* cmd, miner, singer: avoid panic if keystore is not available

* cmd/geth: print warning instead of panic

## Patch
### cmd/geth/accountcmd.go
```diff
@@ -301,7 +301,11 @@ func accountUpdate(ctx *cli.Context) error {
 		utils.Fatalf("No accounts specified to update")
 	}
 	stack, _ := makeConfigNode(ctx)
-	ks := stack.AccountManager().Backends(keystore.KeyStoreType)[0].(*keystore.KeyStore)
+	backends := stack.AccountManager().Backends(keystore.KeyStoreType)
+	if len(backends) == 0 {
+		utils.Fatalf("Keystore is not available")
+	}
+	ks := backends[0].(*keystore.KeyStore)
 
 	for _, addr := range ctx.Args().Slice() {
 		account, oldPassword := unlockAccount(ks, addr, 0, nil)
@@ -326,7 +330,11 @@ func importWallet(ctx *cli.Context) error {
 	stack, _ := makeConfigNode(ctx)
 	passphrase := utils.GetPassPhraseWithList("", false, 0, utils.MakePasswordList(ctx))
 
-	ks := stack.AccountManager().Backends(keystore.KeyStoreType)[0].(*keystore.KeyStore)
+	backends := stack.AccountManager().Backends(keystore.KeyStoreType)
+	if len(backends) == 0 {
+		utils.Fatalf("Keystore is not available")
+	}
+	ks := backends[0].(*keystore.KeyStore)
 	acct, err := ks.ImportPreSaleKey(keyJSON, passphrase)
 	if err != nil {
 		utils.Fatalf("%v", err)
@@ -347,7 +355,11 @@ func accountImport(ctx *cli.Context) error {
 	stack, _ := makeConfigNode(ctx)
 	passphrase := utils.GetPassPhraseWithList("Your new account is locked with a password. Please give a password. Do not forget this password.", true, 0, utils.MakePasswordList(ctx))
 
-	ks := stack.AccountManager().Backends(keystore.KeyStoreType)[0].(*keystore.KeyStore)
+	backends := stack.AccountManager().Backends(keystore.KeyStoreType)
+	if len(backends) == 0 {
+		utils.Fatalf("Keystore is not available")
+	}
+	ks := backends[0].(*keystore.KeyStore)
 	acct, err := ks.ImportECDSA(key, passphrase)
 	if err != nil {
 		utils.Fatalf("Could not create the account: %v", err)
```

### cmd/geth/main.go
```diff
@@ -464,7 +464,12 @@ func unlockAccounts(ctx *cli.Context, stack *node.Node) {
 	if !stack.Config().InsecureUnlockAllowed && stack.Config().ExtRPCEnabled() {
 		utils.Fatalf("Account unlock with HTTP access is forbidden!")
 	}
-	ks := stack.AccountManager().Backends(keystore.KeyStoreType)[0].(*keystore.KeyStore)
+	backends := stack.AccountManager().Backends(keystore.KeyStoreType)
+	if len(backends) == 0 {
+		log.Warn("Failed to unlock accounts, keystore is not available")
+		return
+	}
+	ks := backends[0].(*keystore.KeyStore)
 	passwords := utils.MakePasswordList(ctx)
 	for i, account := range unlocks {
 		unlockAccount(ks, account, i, passwords)
```

### miner/stress/beacon/main.go
```diff
@@ -127,7 +127,11 @@ func newNode(typ nodetype, genesis *core.Genesis, enodes []*enode.Node) *ethNode
 
 	// Inject the signer key and start sealing with it
 	stack.AccountManager().AddBackend(keystore.NewPlaintextKeyStore("beacon-stress"))
-	store := stack.AccountManager().Backends(keystore.KeyStoreType)[0].(*keystore.KeyStore)
+	ks := stack.AccountManager().Backends(keystore.KeyStoreType)
+	if len(ks) == 0 {
+		panic("Keystore is not available")
+	}
+	store := ks[0].(*keystore.KeyStore)
 	if _, err := store.NewAccount(""); err != nil {
 		panic(err)
 	}
```

### signer/core/uiapi.go
```diff
@@ -111,7 +111,11 @@ func (s *UIServerAPI) DeriveAccount(url string, path string, pin *bool) (account
 
 // fetchKeystore retrieves the encrypted keystore from the account manager.
 func fetchKeystore(am *accounts.Manager) *keystore.KeyStore {
-	return am.Backends(keystore.KeyStoreType)[0].(*keystore.KeyStore)
+	ks := am.Backends(keystore.KeyStoreType)
+	if len(ks) == 0 {
+		return nil
+	}
+	return ks[0].(*keystore.KeyStore)
 }
 
 // ImportRawKey stores the given hex encoded ECDSA key into the key directory,
```
