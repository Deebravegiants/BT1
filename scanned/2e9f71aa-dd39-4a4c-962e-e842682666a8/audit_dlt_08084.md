# [?] btcec/signature: fix DoS bug with signature parsing

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2018-09-20
Source: https://github.com/btcsuite/btcd/commit/db8e412dc620fe7b53fe320c473b6d5fa1810772
Type: security-commit

## Details
btcec/signature: fix DoS bug with signature parsing

## Patch
### btcec/signature.go
```diff
@@ -112,7 +112,10 @@ func parseSig(sigStr []byte, curve elliptic.Curve, der bool) (*Signature, error)
 	// length of remaining message
 	siglen := sigStr[index]
 	index++
-	if int(siglen+2) > len(sigStr) {
+
+	// siglen should be less than the entire message and greater than
+	// the minimal message of size 8.
+	if int(siglen+2) > len(sigStr) || int(siglen+2) < 8 {
 		return nil, errors.New("malformed signature: bad length")
 	}
 	// trim the slice we're working on so we only look at what matters.
```

### btcec/signature_test.go
```diff
@@ -113,6 +113,12 @@ var signatureTests = []signatureTest{
 		der:     true,
 		isValid: false,
 	},
+	{
+		name:    "invalid message length",
+		sig:     []byte{0x30, 0x00, 0x02, 0x01, 0x00, 0x02, 0x01, 0x00},
+		der:     false,
+		isValid: false,
+	},
 	{
 		name: "long len",
 		sig: []byte{0x30, 0x45, 0x02, 0x20, 0x4e, 0x45, 0xe1, 0x69,
```
