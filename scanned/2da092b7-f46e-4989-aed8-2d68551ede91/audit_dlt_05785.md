# [?] fix(crypto): panic: encoding: unsupported key {0xc015dcc0c0} (#3702)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-08-14
Source: https://github.com/cometbft/cometbft/commit/6690e2f0862aa9c9b8361c0b4238680e601f2649
Type: security-commit

## Details
fix(crypto): panic: encoding: unsupported key {0xc015dcc0c0} (#3702)

Closes #3699

---

#### PR checklist

- [ ] ~~Tests written/updated~~
- [ ] ~~Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)~~
- [x] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [x] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

---------

Co-authored-by: Sergio Mena <sergio@informal.systems>

## Patch
### crypto/encoding/codec.go
```diff
@@ -2,6 +2,7 @@ package encoding
 
 import (
 	"fmt"
+	"reflect"
 
 	pc "github.com/cometbft/cometbft/api/cometbft/crypto/v1"
 	"github.com/cometbft/cometbft/crypto"
@@ -14,11 +15,11 @@ import (
 // ErrUnsupportedKey describes an error resulting from the use of an
 // unsupported key in [PubKeyToProto] or [PubKeyFromProto].
 type ErrUnsupportedKey struct {
-	Key any
+	KeyType string
 }
 
 func (e ErrUnsupportedKey) Error() string {
-	return fmt.Sprintf("encoding: unsupported key %v", e.Key)
+	return "encoding: unsupported key " + e.KeyType
 }
 
 // ErrInvalidKeyLen describes an error resulting from the use of a key with
@@ -41,7 +42,8 @@ func init() {
 	}
 }
 
-// PubKeyToProto takes crypto.PubKey and transforms it to a protobuf Pubkey.
+// PubKeyToProto takes crypto.PubKey and transforms it to a protobuf Pubkey. It
+// returns ErrUnsupportedKey if the pubkey type is unsupported.
 func PubKeyToProto(k crypto.PubKey) (pc.PublicKey, error) {
 	var kp pc.PublicKey
 	switch k := k.(type) {
@@ -57,9 +59,9 @@ func PubKeyToProto(k crypto.PubKey) (pc.PublicKey, error) {
 				Secp256K1: k,
 			},
 		}
-	case *bls12381.PubKey:
+	case *bls12381.PubKey, bls12381.PubKey:
 		if !bls12381.Enabled {
-			return kp, ErrUnsupportedKey{Key: k}
+			return kp, ErrUnsupportedKey{KeyType: bls12381.KeyType}
 		}
 
 		kp = pc.PublicKey{
@@ -68,12 +70,19 @@ func PubKeyToProto(k crypto.PubKey) (pc.PublicKey, error) {
 			},
 		}
 	default:
-		return kp, ErrUnsupportedKey{Key: k}
+		kt := reflect.TypeOf(k)
+		if kt == nil {
+			return kp, ErrUnsupportedKey{KeyType: "<nil>"}
+		} else {
+			return kp, ErrUnsupportedKey{KeyType: kt.String()}
+		}
 	}
 	return kp, nil
 }
 
-// PubKeyFromProto takes a protobuf Pubkey and transforms it to a crypto.Pubkey.
+// PubKeyFromProto takes a protobuf Pubkey and transforms it to a
+// crypto.Pubkey. It returns ErrUnsupportedKey if the pubkey type is
+// unsupported or ErrInvalidKeyLen if the key length is invalid.
 func PubKeyFromProto(k pc.PublicKey) (crypto.PubKey, error) {
 	switch k := k.Sum.(type) {
 	case *pc.PublicKey_Ed25519:
@@ -100,7 +109,7 @@ func PubKeyFromProto(k pc.PublicKey) (crypto.PubKey, error) {
 		return pk, nil
 	case *pc.PublicKey_Bls12381:
 		if !bls12381.Enabled {
-			return nil, ErrUnsupportedKey{Key: k}
+			return nil, ErrUnsupportedKey{KeyType: bls12381.KeyType}
 		}
 
 		if len(k.Bls12381) != bls12381.PubKeySize {
@@ -112,13 +121,18 @@ func PubKeyFromProto(k pc.PublicKey) (crypto.PubKey, error) {
 		}
 		return bls12381.NewPublicKeyFromBytes(k.Bls12381)
 	default:
-		return nil, ErrUnsupportedKey{Key: k}
+		kt := reflect.TypeOf(k)
+		if kt == nil {
+			return nil, ErrUnsupportedKey{KeyType: "<nil>"}
+		} else {
+			return nil, ErrUnsupportedKey{KeyType: kt.String()}
+		}
 	}
 }
 
-// PubKeyFromTypeAndBytes builds a crypto.PubKey from the given type
-// and bytes. It returns ErrUnsupportedKey if the pubkey type is
-// unsupported.
+// PubKeyFromTypeAndBytes builds a crypto.PubKey from the given type and bytes.
+// It returns ErrUnsupportedKey if the pubkey type is unsupported or
+// ErrInvalidKeyLen if the key length is invalid.
 func PubKeyFromTypeAndBytes(pkType string, bytes []byte) (crypto.PubKey, error) {
 	var pubKey crypto.PubKey
 	switch pkType {
@@ -148,7 +162,7 @@ func PubKeyFromTypeAndBytes(pkType string, bytes []byte) (crypto.PubKey, error)
 		pubKey = pk
 	case bls12381.KeyType:
 		if !bls12381.Enabled {
-			return nil, ErrUnsupportedKey{Key: pkType}
+			return nil, ErrUnsupportedKey{KeyType: pkType}
 		}
 
 		if len(bytes) != bls12381.PubKeySize {
@@ -161,7 +175,7 @@ func PubKeyFromTypeAndBytes(pkType string, bytes []byte) (crypto.PubKey, error)
 
 		return bls12381.NewPublicKeyFromBytes(bytes)
 	default:
-		return nil, ErrUnsupportedKey{Key: pkType}
+		return nil, ErrUnsupportedKey{KeyType: pkType}
 	}
 	return pubKey, nil
 }
```

### crypto/encoding/codec_test.go
```diff
@@ -6,11 +6,19 @@ import (
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
 
+	"github.com/cometbft/cometbft/crypto"
 	"github.com/cometbft/cometbft/crypto/bls12381"
 	"github.com/cometbft/cometbft/crypto/ed25519"
 	"github.com/cometbft/cometbft/crypto/secp256k1"
 )
 
+type unsupportedPubKey struct{}
+
+func (unsupportedPubKey) Address() crypto.Address             { return nil }
+func (unsupportedPubKey) Bytes() []byte                       { return nil }
+func (unsupportedPubKey) VerifySignature([]byte, []byte) bool { return false }
+func (unsupportedPubKey) Type() string                        { return "unsupportedPubKey" }
+
 func TestPubKeyToFromProto(t *testing.T) {
 	// ed25519
 	pk := ed25519.GenPrivKey().PubKey()
@@ -46,6 +54,11 @@ func TestPubKeyToFromProto(t *testing.T) {
 		_, err = PubKeyToProto(bls12381.PubKey{})
 		assert.Error(t, err)
 	}
+
+	// unsupported key type
+	_, err = PubKeyToProto(unsupportedPubKey{})
+	require.Error(t, err)
+	assert.Equal(t, ErrUnsupportedKey{KeyType: "encoding.unsupportedPubKey"}, err)
 }
 
 func TestPubKeyFromTypeAndBytes(t *testing.T) {
```

### types/validator.go
```diff
@@ -120,10 +120,15 @@ func ValidatorListString(vals []*Validator) string {
 // These are the bytes that gets hashed in consensus. It excludes address
 // as its redundant with the pubkey. This also excludes ProposerPriority
 // which changes every round.
+//
+// If the public key is unsupported, it returns nil. Caller must handle `nil`
+// as it would handle an error.
 func (v *Validator) Bytes() []byte {
 	pk, err := ce.PubKeyToProto(v.PubKey)
 	if err != nil {
-		panic(err)
+		// Unsupported key.
+		// Since this is used by the light client, we should not panic here.
+		return nil
 	}
 
 	pbv := cmtproto.SimpleValidator{
```
