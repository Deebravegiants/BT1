# [?] fix panic on inner error length

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-09-11
Source: https://github.com/smartcontractkit/ccip/commit/f778658820913d5e2492d9ac83a3fb5bbb0b384e
Type: security-commit

## Details
fix panic on inner error length

## Patch
### core/scripts/ccip/revert-reason/handler/reason.go
```diff
@@ -79,6 +79,9 @@ func DecodeErrorStringFromABI(errorString string) (string, error) {
 					// Get the inner type, which is `bytes`
 					fmt.Printf("Error is \"%v\" inner error: ", errorName)
 					errorBytes := v.([]interface{})[0].([]byte)
+					if len(errorBytes) < 4 {
+						return "[reverted without error code]", nil
+					}
 					return DecodeErrorStringFromABI(hex.EncodeToString(errorBytes))
 				}
 				return fmt.Sprintf("error is \"%v\" args %v\n", errorName, v), nil
```
