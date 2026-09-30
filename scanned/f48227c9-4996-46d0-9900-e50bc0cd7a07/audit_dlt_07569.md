# [?] signer/core: prevent nil pointer panics in keystore operations (#33829)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-03-06
Source: https://github.com/ethereum/go-ethereum/commit/0d043d071e7a6bb63a49c7d8499c339f531c83ad
Type: security-commit

## Details
signer/core: prevent nil pointer panics in keystore operations (#33829)

Add nil checks to prevent potential panics when keystore backend is
unavailable in the Clef signer API.

## Patch
### signer/core/uiapi.go
```diff
@@ -73,8 +73,9 @@ type rawWallet struct {
 // Example call
 // {"jsonrpc":"2.0","method":"clef_listWallets","params":[], "id":5}
 func (api *UIServerAPI) ListWallets() []rawWallet {
-	wallets := make([]rawWallet, 0) // return [] instead of nil if empty
-	for _, wallet := range api.am.Wallets() {
+	allWallets := api.am.Wallets()
+	wallets := make([]rawWallet, 0, len(allWallets)) // return [] instead of nil if empty
+	for _, wallet := range allWallets {
 		status, failure := wallet.Status()
 
 		raw := rawWallet{
@@ -130,8 +131,12 @@ func (api *UIServerAPI) ImportRawKey(privkey string, password string) (accounts.
 	if err := ValidatePasswordFormat(password); err != nil {
 		return accounts.Account{}, fmt.Errorf("password requirements not met: %v", err)
 	}
+	ks := fetchKeystore(api.am)
+	if ks == nil {
+		return accounts.Account{}, errors.New("password based accounts not supported")
+	}
 	// No error
-	return fetchKeystore(api.am).ImportECDSA(key, password)
+	return ks.ImportECDSA(key, password)
 }
 
 // OpenWallet initiates a hardware wallet opening procedure, establishing a USB
```
