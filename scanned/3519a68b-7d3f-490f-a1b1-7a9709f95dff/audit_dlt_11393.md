# [?] fix: align challenge name, prepending with zeros to avoid field overflow

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark-crypto
Published: 2023-01-12
Source: https://github.com/Consensys-Incorporated/gnark-crypto/commit/0fc86727e9a0a0b609c6a6d9a750c10890b0d675
Type: security-commit

## Details
fix: align challenge name, prepending with zeros to avoid field overflow

## Patch
### fiat-shamir/transcript.go
```diff
@@ -16,6 +16,7 @@ package fiatshamir
 
 import (
 	"errors"
+	"fmt"
 	"hash"
 )
 
@@ -83,7 +84,7 @@ func (t *Transcript) Bind(challengeID string, bValue []byte) error {
 // ComputeChallenge computes the challenge corresponding to the given name.
 // The challenge is:
 // * H(name || previous_challenge || binded_values...) if the challenge is not the first one
-// * H(name || binded_values... ) if it's is the first challenge
+// * H(name || binded_values... ) if it is the first challenge
 func (t *Transcript) ComputeChallenge(challengeID string) ([]byte, error) {
 
 	challenge, ok := t.challenges[challengeID]
@@ -101,7 +102,12 @@ func (t *Transcript) ComputeChallenge(challengeID string) ([]byte, error) {
 	defer t.h.Reset()
 
 	// write the challenge name, the purpose is to have a domain separator
-	bName := []byte(challengeID)
+	bName := make([]byte, t.h.BlockSize())
+	if len(challengeID) < len(bName) { // strict inequality because don't even want to have to deal with modular reduction in case of arithmetic hashes TODO: Replace with strict
+		copy(bName[len(bName)-len(challengeID):], challengeID)
+	} else {
+		return nil, fmt.Errorf("challenge name too large")
+	}
 	if _, err := t.h.Write(bName); err != nil {
 		return nil, err
 	}
```
