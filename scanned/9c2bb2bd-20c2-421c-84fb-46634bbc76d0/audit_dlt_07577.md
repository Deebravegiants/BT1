# [?] fixes missing protection of nil pointer dereference in scwallet (#32186)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-08-21
Source: https://github.com/ethereum/go-ethereum/commit/39ab721992e634f3b0adb3e08b16fb0c4d8a379c
Type: security-commit

## Details
fixes missing protection of nil pointer dereference in scwallet (#32186)

Fixes #32181

Signed-off-by: kapil <kapilsareen584@gmail.com>

## Patch
### accounts/scwallet/wallet.go
```diff
@@ -472,6 +472,11 @@ func (w *Wallet) selfDerive() {
 			continue
 		}
 		pairing := w.Hub.pairing(w)
+		if pairing == nil {
+			w.lock.Unlock()
+			reqc <- struct{}{}
+			continue
+		}
 
 		// Device lock obtained, derive the next batch of accounts
 		var (
@@ -631,13 +636,13 @@ func (w *Wallet) Derive(path accounts.DerivationPath, pin bool) (accounts.Accoun
 	}
 
 	if pin {
-		pairing := w.Hub.pairing(w)
-		pairing.Accounts[account.Address] = path
-		if err := w.Hub.setPairing(w, pairing); err != nil {
-			return accounts.Account{}, err
+		if pairing := w.Hub.pairing(w); pairing != nil {
+			pairing.Accounts[account.Address] = path
+			if err := w.Hub.setPairing(w, pairing); err != nil {
+				return accounts.Account{}, err
+			}
 		}
 	}
-
 	return account, nil
 }
 
@@ -774,11 +779,11 @@ func (w *Wallet) SignTxWithPassphrase(account accounts.Account, passphrase strin
 // It first checks for the address in the list of pinned accounts, and if it is
 // not found, attempts to parse the derivation path from the account's URL.
 func (w *Wallet) findAccountPath(account accounts.Account) (accounts.DerivationPath, error) {
-	pairing := w.Hub.pairing(w)
-	if path, ok := pairing.Accounts[account.Address]; ok {
-		return path, nil
+	if pairing := w.Hub.pairing(w); pairing != nil {
+		if path, ok := pairing.Accounts[account.Address]; ok {
+			return path, nil
+		}
 	}
-
 	// Look for the path in the URL
 	if account.URL.Scheme != w.Hub.scheme {
 		return nil, fmt.Errorf("scheme %s does not match wallet scheme %s", account.URL.Scheme, w.Hub.scheme)
```
