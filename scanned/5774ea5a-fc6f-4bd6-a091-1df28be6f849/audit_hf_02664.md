# [M] Lack Of Size Checks In createUUID() Function

## Summary
Severity: Medium
Contest weight: 0.0978
Dataset id: 14441
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Generation of UUID from a public key may result in unhandled out-of-bounds panic.
There are no size checks implemented to ensure len(keyBytes) > 16:
```go
func createUUID(key string) (string, error) {
    uuidBytes := make([]byte, 16)
    keyBytes := []byte(key)
    copy(uuidBytes, keyBytes[len(keyBytes)-16:len(keyBytes)])
}
```
If len(keyBytes) is less than 16, the keyBytes[len(keyBytes)-16:len(keyBytes)] will trigger an unhandled panic.
As the public key is taken from keysign2.Request of external source via TSS node’s keysignHandler(), this could potentially be triggered via a malformed incoming request.

## Recommendation
Implement checks to verify that len(keyBytes) > 16 prior to taking a slice of keyBytes.
