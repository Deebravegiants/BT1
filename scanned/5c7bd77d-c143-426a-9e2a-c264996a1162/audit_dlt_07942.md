# [?] fix(secp256k1): compute key address and bytes eagerly to avoid data race (#5921)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2026-09-09
Source: https://github.com/ava-labs/avalanchego/commit/57f3d1ac9c1a0e3ea43024ffd582a41269b80d43
Type: security-commit

## Details
fix(secp256k1): compute key address and bytes eagerly to avoid data race (#5921)

## Patch
### utils/crypto/secp256k1/BUILD.bazel
```diff
@@ -31,10 +31,12 @@ go_test(
     ],
     embed = [":secp256k1"],
     deps = [
+        "//ids",
         "//utils",
         "//utils/cb58",
         "//utils/hashing",
         "@com_github_decred_dcrd_dcrec_secp256k1_v4//:secp256k1",
+        "@com_github_stretchr_testify//assert",
         "@com_github_stretchr_testify//require",
     ],
 )
```

### utils/crypto/secp256k1/secp256k1.go
```diff
@@ -58,7 +58,10 @@ var (
 
 func NewPrivateKey() (*PrivateKey, error) {
 	k, err := secp256k1.GeneratePrivateKey()
-	return &PrivateKey{sk: k}, err
+	if err != nil {
+		return nil, err
+	}
+	return newPrivateKey(k), nil
 }
 
 func ToPublicKey(b []byte) (*PublicKey, error) {
@@ -67,20 +70,17 @@ func ToPublicKey(b []byte) (*PublicKey, error) {
 	}
 
 	key, err := secp256k1.ParsePubKey(b)
-	return &PublicKey{
-		pk:    key,
-		bytes: b,
-	}, err
+	if err != nil {
+		return nil, err
+	}
+	return newPublicKey(key), nil
 }
 
 func ToPrivateKey(b []byte) (*PrivateKey, error) {
 	if len(b) != PrivateKeyLen {
 		return nil, errInvalidPrivateKeyLength
 	}
-	return &PrivateKey{
-		sk:    secp256k1.PrivKeyFromBytes(b),
-		bytes: b,
-	}, nil
+	return newPrivateKey(secp256k1.PrivKeyFromBytes(b)), nil
 }
 
 func RecoverPublicKey(msg, sig []byte) (*PublicKey, error) {
@@ -106,7 +106,7 @@ func RecoverPublicKeyFromHash(hash, sig []byte) (*PublicKey, error) {
 		return nil, errCompressed
 	}
 
-	return &PublicKey{pk: rawPubkey}, nil
+	return newPublicKey(rawPubkey), nil
 }
 
 type RecoverCache struct {
@@ -146,12 +146,25 @@ func (r *RecoverCache) RecoverPublicKeyFromHash(hash, sig []byte) (*PublicKey, e
 	return pubKey, nil
 }
 
+// A PublicKey is an immutable secp256k1 public key. It is safe for concurrent
+// use, which allows a single instance to be shared, e.g. via [RecoverCache].
 type PublicKey struct {
 	pk    *secp256k1.PublicKey
 	addr  ids.ShortID
 	bytes []byte
 }
 
+// newPublicKey computes the compressed serialization and address eagerly so
+// that the returned key is never mutated after construction.
+func newPublicKey(pk *secp256k1.PublicKey) *PublicKey {
+	bytes := pk.SerializeCompressed()
+	return &PublicKey{
+		pk:    pk,
+		addr:  ids.ShortID(hashing.ComputeHash160Array(hashing.ComputeHash256(bytes))),
+		bytes: bytes,
+	}
+}
+
 func (k *PublicKey) Verify(msg, sig []byte) bool {
 	return k.VerifyHash(hashing.ComputeHash256(msg), sig)
 }
@@ -170,37 +183,38 @@ func (k *PublicKey) ToECDSA() *stdecdsa.PublicKey {
 }
 
 func (k *PublicKey) Address() ids.ShortID {
-	if k.addr == ids.ShortEmpty {
-		addr, err := ids.ToShortID(hashing.PubkeyBytesToAddress(k.Bytes()))
-		if err != nil {
-			panic(err)
-		}
-		k.addr = addr
-	}
 	return k.addr
 }
 
 func (k *PublicKey) EthAddress() common.Address {
 	return crypto.PubkeyToAddress(*(k.ToECDSA()))
 }
 
+// Bytes returns the compressed serialization of the key. The returned slice
+// is shared and MUST NOT be modified.
 func (k *PublicKey) Bytes() []byte {
-	if k.bytes == nil {
-		k.bytes = k.pk.SerializeCompressed()
-	}
 	return k.bytes
 }
 
+// A PrivateKey is a secp256k1 private key. Its public key and serialization
+// are computed at construction, so its accessors are safe for concurrent use.
 type PrivateKey struct {
 	sk    *secp256k1.PrivateKey
 	pk    *PublicKey
 	bytes []byte
 }
 
-func (k *PrivateKey) PublicKey() *PublicKey {
-	if k.pk == nil {
-		k.pk = &PublicKey{pk: k.sk.PubKey()}
+// newPrivateKey computes the public key and serialization eagerly so that
+// the returned key is never mutated after construction.
+func newPrivateKey(sk *secp256k1.PrivateKey) *PrivateKey {
+	return &PrivateKey{
+		sk:    sk,
+		pk:    newPublicKey(sk.PubKey()),
+		bytes: sk.Serialize(),
 	}
+}
+
+func (k *PrivateKey) PublicKey() *PublicKey {
 	return k.pk
 }
 
@@ -226,10 +240,9 @@ func (k *PrivateKey) ToECDSA() *stdecdsa.PrivateKey {
 	return k.sk.ToECDSA()
 }
 
+// Bytes returns the serialized private key. The returned slice is shared and
+// MUST NOT be modified.
 func (k *PrivateKey) Bytes() []byte {
-	if k.bytes == nil {
-		k.bytes = k.sk.Serialize()
-	}
 	return k.bytes
 }
 
@@ -283,10 +296,7 @@ func (k *PrivateKey) unmarshalText(text string) error {
 		return errInvalidPrivateKeyLength
 	}
 
-	*k = PrivateKey{
-		sk:    secp256k1.PrivKeyFromBytes(keyBytes),
-		bytes: keyBytes,
-	}
+	*k = *newPrivateKey(secp256k1.PrivKeyFromBytes(keyBytes))
 	return nil
 }
 
```

### utils/crypto/secp256k1/secp256k1_test.go
```diff
@@ -4,10 +4,13 @@
 package secp256k1
 
 import (
+	"sync"
 	"testing"
 
+	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
 
+	"github.com/ava-labs/avalanchego/ids"
 	"github.com/ava-labs/avalanchego/utils/cb58"
 	"github.com/ava-labs/avalanchego/utils/hashing"
 
@@ -53,6 +56,45 @@ func TestCachedRecover(t *testing.T) {
 	require.Equal(key.PublicKey(), pub2)
 }
 
+// TestConcurrentAccess checks that keys are safe for concurrent use. This
+// test is not meaningful without the race detector
+func TestConcurrentAccess(t *testing.T) {
+	sk, want := TestKeys()[0], TestKeys()[0]
+
+	msg := []byte{1, 2, 3}
+	sig, err := sk.Sign(msg)
+	require.NoError(t, err, "Sign()")
+
+	cache := NewRecoverCache(1)
+	cached, err := cache.RecoverPublicKey(msg, sig)
+	require.NoError(t, err, "RecoverPublicKey()")
+
+	type key interface {
+		Address() ids.ShortID
+		Bytes() []byte
+	}
+	tests := []struct {
+		name string
+		key  key
+		want key
+	}{
+		{name: "PrivateKey", key: sk, want: want},
+		{name: "cached PublicKey", key: cached, want: want.PublicKey()},
+	}
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			var wg sync.WaitGroup
+			for range 8 {
+				wg.Go(func() {
+					assert.Equal(t, tt.want.Address(), tt.key.Address(), "Address()")
+					assert.Equal(t, tt.want.Bytes(), tt.key.Bytes(), "Bytes()")
+				})
+			}
+			wg.Wait()
+		})
+	}
+}
+
 func TestExtensive(t *testing.T) {
 	require := require.New(t)
 
@@ -255,9 +297,7 @@ func TestExportedMethods(t *testing.T) {
 	key := TestKeys()[0]
 
 	pubKey := key.PublicKey()
-	require.Equal("111111111111111111116DBWJs", pubKey.addr.String())
 	require.Equal("Q4MzFZZDPHRPAHFeDs3NiyyaZDvxHKivf", pubKey.Address().String())
-	require.Equal("Q4MzFZZDPHRPAHFeDs3NiyyaZDvxHKivf", pubKey.addr.String())
 	require.Equal("Q4MzFZZDPHRPAHFeDs3NiyyaZDvxHKivf", key.Address().String())
 
 	expectedPubKeyBytes := []byte{
@@ -267,7 +307,7 @@ func TestExportedMethods(t *testing.T) {
 		0xfb, 0x03, 0xda, 0x6f, 0x4d, 0xbc, 0x94, 0x35,
 		0x7d,
 	}
-	require.Equal(expectedPubKeyBytes, pubKey.bytes)
+	require.Equal(expectedPubKeyBytes, pubKey.Bytes())
 
 	expectedPubKey, err := ToPublicKey(expectedPubKeyBytes)
 	require.NoError(err)
```
