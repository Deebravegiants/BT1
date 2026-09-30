# [?] fix(t/tx): fix data race for "err" shared variable in getSignersFunc (#24344)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-04-03
Source: https://github.com/cosmos/cosmos-sdk/commit/d6f3ede8dc1174d1a22a0d10bfd352e32264bd56
Type: security-commit

## Details
fix(t/tx): fix data race for "err" shared variable in getSignersFunc (#24344)

Co-authored-by: Alex | Interchain Labs <alex@interchainlabs.io>

## Patch
### x/tx/signing/context.go
```diff
@@ -307,7 +307,10 @@ func (c *Context) makeGetSignersFunc(descriptor protoreflect.MessageDescriptor)
 	}
 
 	return func(message proto.Message) ([][]byte, error) {
-		var signers [][]byte
+		var (
+			signers [][]byte
+			err     error
+		)
 		for _, getter := range fieldGetters {
 			signers, err = getter(message, signers)
 			if err != nil {
```
