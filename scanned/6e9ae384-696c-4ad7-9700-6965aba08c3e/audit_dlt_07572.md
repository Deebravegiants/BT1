# [?] accounts/scwallet: fix panic in decryptAPDU (#33606)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-01-20
Source: https://github.com/ethereum/go-ethereum/commit/46d804776b4e93eda4c4da14fb8e2fd77d4670ea
Type: security-commit

## Details
accounts/scwallet: fix panic in decryptAPDU (#33606)

Validate ciphertext length in decryptAPDU, preventing runtime panics on
invalid input.

## Patch
### accounts/scwallet/securechannel.go
```diff
@@ -300,6 +300,10 @@ func (s *SecureChannelSession) decryptAPDU(data []byte) ([]byte, error) {
 		return nil, err
 	}
 
+	if len(data) == 0 || len(data)%aes.BlockSize != 0 {
+		return nil, fmt.Errorf("invalid ciphertext length: %d", len(data))
+	}
+
 	ret := make([]byte, len(data))
 
 	crypter := cipher.NewCBCDecrypter(a, s.iv)
```
