# [?] fix(builder): potential nil panic

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-04-23
Source: https://github.com/berachain/beacon-kit/commit/f91bd31fe1dcf74a4bec33d3295b9632ab7bacfd
Type: security-commit

## Details
fix(builder): potential nil panic

## Patch
### mod/payload/builder/payload.go
```diff
@@ -106,6 +106,8 @@ func (pb *PayloadBuilder) RequestPayloadAndWait(
 	)
 	if err != nil {
 		return nil, err
+	} else if payloadID == nil {
+		return nil, ErrNilPayloadID
 	}
 
 	// Wait for the payload to be delivered to the execution client.
```
