# [?] Merge pull request #1301 from meyer9/fix-sig-dos

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2018-09-24
Source: https://github.com/btcsuite/btcd/commit/2a560b2036bee5e3679ec2133eb6520b2f195213
Type: security-commit

## Details
Merge pull request #1301 from meyer9/fix-sig-dos

btcec/signature: fix DoS bug with signature parsing

## Patch
### btcec/signature.go
```diff
@@ -85,6 +85,11 @@ func (sig *Signature) IsEqual(otherSig *Signature) bool {
 		sig.S.Cmp(otherSig.S) == 0
 }
 
+// minSigLen is the minimum length of a DER encoded signature and is
+// when both R and S are 1 byte each.
+// 0x30 + <1-byte> + 0x02 + 0x01 + <byte> + 0x2 + 0x01 + <byte>
+const minSigLen = 8
+
 func parseSig(sigStr []byte, curve elliptic.Curve, der bool) (*Signature, error) {
 	// Originally this code used encoding/asn1 in order to parse the
 	// signature, but a number of problems were found with this approach.
@@ -98,9 +103,7 @@ func parseSig(sigStr []byte, curve elliptic.Curve, der bool) (*Signature, error)
 
 	signature := &Signature{}
 
-	// minimal message is when both numbers are 1 bytes. adding up to:
-	// 0x30 + len + 0x02 + 0x01 + <byte> + 0x2 + 0x01 + <byte>
-	if len(sigStr) < 8 {
+	if len(sigStr) < minSigLen {
 		return nil, errors.New("malformed signature: too short")
 	}
 	// 0x30
@@ -112,7 +115,10 @@ func parseSig(sigStr []byte, curve elliptic.Curve, der bool) (*Signature, error)
 	// length of remaining message
 	siglen := sigStr[index]
 	index++
-	if int(siglen+2) > len(sigStr) {
+
+	// siglen should be less than the entire message and greater than
+	// the minimal message size.
+	if int(siglen+2) > len(sigStr) || int(siglen+2) < minSigLen {
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
