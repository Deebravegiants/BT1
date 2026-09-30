# [?] accounts/keystore: fix panic in decryptPreSaleKey (#33602)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-01-14
Source: https://github.com/ethereum/go-ethereum/commit/94710f79a21fb64299555a545113545677e5dfbe
Type: security-commit

## Details
accounts/keystore: fix panic in decryptPreSaleKey (#33602)

Validate ciphertext length in decryptPreSaleKey, preventing runtime
panics on invalid input.

## Patch
### accounts/keystore/presale.go
```diff
@@ -81,6 +81,9 @@ func decryptPreSaleKey(fileContent []byte, password string) (key *Key, err error
 	*/
 	passBytes := []byte(password)
 	derivedKey := pbkdf2.Key(passBytes, passBytes, 2000, 16, sha256.New)
+	if len(cipherText)%aes.BlockSize != 0 {
+		return nil, errors.New("ciphertext must be a multiple of block size")
+	}
 	plainText, err := aesCBCDecrypt(derivedKey, cipherText, iv)
 	if err != nil {
 		return nil, err
```
