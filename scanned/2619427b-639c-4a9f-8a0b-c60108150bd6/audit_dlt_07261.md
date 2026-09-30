# [?] crypto/secp256k1: Fix signature malleability, adopt more efficient en… (#2239)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2018-08-28
Source: https://github.com/cometbft/cometbft/commit/b1bc3e4f894c840d7b311af28fc9e1c58bbc8769
Type: security-commit

## Details
crypto/secp256k1: Fix signature malleability, adopt more efficient en… (#2239)

* crypto/secp256k1: Fix signature malleability, adopt more efficient encoding

This removes signature malleability per ADR 14, and makes secp match
the encoding in ADR 15.

* (squash this) add lock

## Patch
### CHANGELOG_PENDING.md
```diff
@@ -14,6 +14,8 @@ BREAKING CHANGES:
 - [crypto] Rename AminoRoute variables to no longer be prefixed by signature type.
 - [config] Replace MaxNumPeers with MaxNumInboundPeers and MaxNumOutboundPeers
 - [node] NewNode now accepts a `*p2p.NodeKey`
+- [crypto] Secp256k1 signature format changed from DER to `r || s`, both little endian encoded as 32 bytes.
+- [crypto] Secp256k1 signature malleability removed by requiring s to be in canonical form. (See ADR 14)
 - [abci] \#2159 Update use of `Validator` ala ADR-018:
     - Remove PubKey from `Validator` and introduce `ValidatorUpdate`
     - InitChain and EndBlock use ValidatorUpdate
```

### Gopkg.lock
```diff
@@ -11,14 +11,14 @@
 
 [[projects]]
   branch = "master"
-  digest = "1:2c00f064ba355903866cbfbf3f7f4c0fe64af6638cc7d1b8bdcf3181bc67f1d8"
+  digest = "1:6aabc1566d6351115d561d038da82a4c19b46c3b6e17f4a0a2fa60260663dc79"
   name = "github.com/btcsuite/btcd"
   packages = ["btcec"]
   pruneopts = "UT"
   revision = "f5e261fc9ec3437697fb31d8b38453c293204b29"
 
 [[projects]]
-  digest = "1:1d8e1cb71c33a9470bbbae09bfec09db43c6bf358dfcae13cd8807c4e2a9a2bf"
+  digest = "1:df684ed7fed3fb406ec421424aaf5fc9c63ccc2f428b25b842da78e634482e4b"
   name = "github.com/btcsuite/btcutil"
   packages = [
     "base58",
@@ -59,7 +59,7 @@
   version = "v1.4.7"
 
 [[projects]]
-  digest = "1:fdf5169073fb0ad6dc12a70c249145e30f4058647bea25f0abd48b6d9f228a11"
+  digest = "1:fa30c0652956e159cdb97dcb2ef8b8db63ed668c02a5c3a40961c8f0641252fe"
   name = "github.com/go-kit/kit"
   packages = [
     "log",
@@ -91,7 +91,7 @@
   version = "v1.7.0"
 
 [[projects]]
-  digest = "1:35621fe20f140f05a0c4ef662c26c0ab4ee50bca78aa30fe87d33120bd28165e"
+  digest = "1:212285efb97b9ec2e20550d81f0446cb7897e57cbdfd7301b1363ab113d8be45"
   name = "github.com/gogo/protobuf"
   packages = [
     "gogoproto",
@@ -106,7 +106,7 @@
   version = "v1.1.1"
 
 [[projects]]
-  digest = "1:17fe264ee908afc795734e8c4e63db2accabaf57326dbf21763a7d6b86096260"
+  digest = "1:cb22af0ed7c72d495d8be1106233ee553898950f15fd3f5404406d44c2e86888"
   name = "github.com/golang/protobuf"
   packages = [
     "proto",
@@ -137,7 +137,7 @@
 
 [[projects]]
   branch = "master"
-  digest = "1:12247a2e99a060cc692f6680e5272c8adf0b8f572e6bce0d7095e624c958a240"
+  digest = "1:8951fe6e358876736d8fa1f3992624fdbb2dec6bc49401c1381d1ef8abbb544f"
   name = "github.com/hashicorp/hcl"
   packages = [
     ".",
@@ -225,7 +225,7 @@
   version = "v1.0.0"
 
 [[projects]]
-  digest = "1:c1a04665f9613e082e1209cf288bf64f4068dcd6c87a64bf1c4ff006ad422ba0"
+  digest = "1:98225904b7abff96c052b669b25788f18225a36673fba022fb93514bb9a2a64e"
   name = "github.com/prometheus/client_golang"
   packages = [
     "prometheus",
@@ -236,15 +236,15 @@
 
 [[projects]]
   branch = "master"
-  digest = "1:2d5cd61daa5565187e1d96bae64dbbc6080dacf741448e9629c64fd93203b0d4"
+  digest = "1:0f37e09b3e92aaeda5991581311f8dbf38944b36a3edec61cc2d1991f527554a"
   name = "github.com/prometheus/client_model"
   packages = ["go"]
   pruneopts = "UT"
   revision = "5c3871d89910bfb32f5fcab2aa4b9ec68e65a99f"
 
 [[projects]]
   branch = "master"
-  digest = "1:63b68062b8968092eb86bedc4e68894bd096ea6b24920faca8b9dcf451f54bb5"
+  digest = "1:dad2e5a2153ee7a6c9ab8fc13673a16ee4fb64434a7da980965a3741b0c981a3"
   name = "github.com/prometheus/common"
   packages = [
     "expfmt",
@@ -256,7 +256,7 @@
 
 [[projects]]
   branch = "master"
-  digest = "1:8c49953a1414305f2ff5465147ee576dd705487c35b15918fcd4efdc0cb7a290"
+  digest = "1:a37c98f4b7a66bb5c539c0539f0915a74ef1c8e0b3b6f45735289d94cae92bfd"
   name = "github.com/prometheus/procfs"
   packages = [
     ".",
@@ -275,7 +275,7 @@
   revision = "e2704e165165ec55d062f5919b4b29494e9fa790"
 
 [[projects]]
-  digest = "1:bd1ae00087d17c5a748660b8e89e1043e1e5479d0fea743352cda2f8dd8c4f84"
+  digest = "1:37ace7f35375adec11634126944bdc45a673415e2fcc07382d03b75ec76ea94c"
   name = "github.com/spf13/afero"
   packages = [
     ".",
@@ -294,7 +294,7 @@
   version = "v1.2.0"
 
 [[projects]]
-  digest = "1:7ffc0983035bc7e297da3688d9fe19d60a420e9c38bef23f845c53788ed6a05e"
+  digest = "1:627ab2f549a6a55c44f46fa24a4307f4d0da81bfc7934ed0473bf38b24051d26"
   name = "github.com/spf13/cobra"
   packages = ["."]
   pruneopts = "UT"
@@ -326,7 +326,7 @@
   version = "v1.0.0"
 
 [[projects]]
-  digest = "1:7e8d267900c7fa7f35129a2a37596e38ed0f11ca746d6d9ba727980ee138f9f6"
+  digest = "1:73697231b93fb74a73ebd8384b68b9a60c57ea6b13c56d2425414566a72c8e6d"
   name = "github.com/stretchr/testify"
   packages = [
     "assert",
@@ -338,7 +338,7 @@
 
 [[projects]]
   branch = "master"
-  digest = "1:b3cfb8d82b1601a846417c3f31c03a7961862cb2c98dcf0959c473843e6d9a2b"
+  digest = "1:922191411ad8f61bcd8018ac127589bb489712c1d1a0ab2497aca4b16de417d2"
   name = "github.com/syndtr/goleveldb"
   packages = [
     "leveldb",
@@ -357,9 +357,16 @@
   pruneopts = "UT"
   revision = "c4c61651e9e37fa117f53c5a906d3b63090d8445"
 
+[[projects]]
+  digest = "1:34a30b75b54e4b73090d0cafc7884950f020272e36813201ba3860822c46c6dd"
+  name = "github.com/tendermint/btcd"
+  packages = ["btcec"]
+  pruneopts = "UT"
+  revision = "e5840949ff4fff0c56f9b6a541e22b63581ea9df"
+
 [[projects]]
   branch = "master"
-  digest = "1:087aaa7920e5d0bf79586feb57ce01c35c830396ab4392798112e8aae8c47722"
+  digest = "1:203b409c21115233a576f99e8f13d8e07ad82b25500491f7e1cca12588fb3232"
   name = "github.com/tendermint/ed25519"
   packages = [
     ".",
@@ -379,7 +386,7 @@
 
 [[projects]]
   branch = "master"
-  digest = "1:c31a37cafc12315b8bd745c8ad6a006ac25350472488162a821e557b3e739d67"
+  digest = "1:df132ec33d5acb4a1ab58d637f1bc3557be49456ca59b9198f5c1e7fa32e0d31"
   name = "golang.org/x/crypto"
   packages = [
     "bcrypt",
@@ -401,7 +408,7 @@
   revision = "56440b844dfe139a8ac053f4ecac0b20b79058f4"
 
 [[projects]]
-  digest = "1:d36f55a999540d29b6ea3c2ea29d71c76b1d9853fdcd3e5c5cb4836f2ba118f1"
+  digest = "1:04dda8391c3e2397daf254ac68003f30141c069b228d06baec8324a5f81dc1e9"
   name = "golang.org/x/net"
   packages = [
     "context",
@@ -418,7 +425,7 @@
 
 [[projects]]
   branch = "master"
-  digest = "1:bb0fe59917bdd5b89f49b9a8b26e5f465e325d9223b3a8e32254314bdf51e0f1"
+  digest = "1:70656e26ab4a96e683a21d677630edb5239a3d60b2d54bdc861c808ab5aa42c7"
   name = "golang.org/x/sys"
   packages = [
     "cpu",
@@ -428,7 +435,7 @@
   revision = "3dc4335d56c789b04b0ba99b7a37249d9b614314"
 
 [[projects]]
-  digest = "1:a2ab62866c75542dd18d2b069fec854577a20211d7c0ea6ae746072a1dccdd18"
+  digest = "1:7509ba4347d1f8de6ae9be8818b0cd1abc3deeffe28aeaf4be6d4b6b5178d9ca"
   name = "golang.org/x/text"
   packages = [
     "collate",
@@ -459,7 +466,7 @@
   revision = "daca94659cb50e9f37c1b834680f2e46358f10b0"
 
 [[projects]]
-  digest = "1:2dab32a43451e320e49608ff4542fdfc653c95dcc35d0065ec9c6c3dd540ed74"
+  digest = "1:4515e3030c440845b046354fd5d57671238428b820deebce2e9dabb5cd3c51ac"
   name = "google.golang.org/grpc"
   packages = [
     ".",
@@ -504,7 +511,6 @@
   analyzer-name = "dep"
   analyzer-version = 1
   input-imports = [
-    "github.com/btcsuite/btcd/btcec",
     "github.com/btcsuite/btcutil/base58",
     "github.com/btcsuite/btcutil/bech32",
     "github.com/ebuchman/fail-test",
@@ -536,6 +542,7 @@
     "github.com/syndtr/goleveldb/leveldb/errors",
     "github.com/syndtr/goleveldb/leveldb/iterator",
     "github.com/syndtr/goleveldb/leveldb/opt",
+    "github.com/tendermint/btcd/btcec",
     "github.com/tendermint/ed25519",
     "github.com/tendermint/ed25519/extra25519",
     "github.com/tendermint/go-amino",
```

### Gopkg.toml
```diff
@@ -85,6 +85,10 @@
   name = "github.com/btcsuite/btcutil"
   revision = "d4cc87b860166d00d6b5b9e0d3b3d71d6088d4d4"
 
+[[constraint]]
+  name = "github.com/tendermint/btcd"
+  revision = "e5840949ff4fff0c56f9b6a541e22b63581ea9df"
+
 # Haven't made a release since 2016.
 [[constraint]]
   name = "github.com/prometheus/client_golang"
```

### crypto/encoding/amino/encode_test.go
```diff
@@ -60,18 +60,20 @@ func ExamplePrintRegisteredTypes() {
 
 func TestKeyEncodings(t *testing.T) {
 	cases := []struct {
-		privKey           crypto.PrivKey
-		privSize, pubSize int // binary sizes
+		privKey                    crypto.PrivKey
+		privSize, pubSize, sigSize int // binary sizes
 	}{
 		{
 			privKey:  ed25519.GenPrivKey(),
 			privSize: 69,
 			pubSize:  37,
+			sigSize:  65,
 		},
 		{
 			privKey:  secp256k1.GenPrivKey(),
 			privSize: 37,
 			pubSize:  38,
+			sigSize:  65,
 		},
 	}
 
@@ -88,7 +90,7 @@ func TestKeyEncodings(t *testing.T) {
 		var sig1, sig2 []byte
 		sig1, err := tc.privKey.Sign([]byte("something"))
 		assert.NoError(t, err, "tc #%d", tcIndex)
-		checkAminoBinary(t, sig1, &sig2, -1) // Signature size changes for Secp anyways.
+		checkAminoBinary(t, sig1, &sig2, tc.sigSize)
 		assert.EqualValues(t, sig1, sig2, "tc #%d", tcIndex)
 
 		// Check (de/en)codings of PubKeys.
```

### crypto/secp256k1/secp256k1.go
```diff
@@ -7,7 +7,7 @@ import (
 	"fmt"
 	"io"
 
-	secp256k1 "github.com/btcsuite/btcd/btcec"
+	secp256k1 "github.com/tendermint/btcd/btcec"
 	amino "github.com/tendermint/go-amino"
 	"github.com/tendermint/tendermint/crypto"
 	"golang.org/x/crypto/ripemd160"
@@ -141,10 +141,12 @@ func (pubKey PubKeySecp256k1) VerifyBytes(msg []byte, sig []byte) bool {
 	if err != nil {
 		return false
 	}
-	parsedSig, err := secp256k1.ParseDERSignature(sig[:], secp256k1.S256())
+	parsedSig, err := secp256k1.ParseSignature(sig[:], secp256k1.S256())
 	if err != nil {
 		return false
 	}
+	// Underlying library ensures that this signature is in canonical form, to
+	// prevent Secp256k1 malleability from altering the sign of the s term.
 	return parsedSig.Verify(crypto.Sha256(msg), pub)
 }
 
```

### crypto/secp256k1/secpk256k1_test.go
```diff
@@ -11,7 +11,7 @@ import (
 	"github.com/tendermint/tendermint/crypto"
 	"github.com/tendermint/tendermint/crypto/secp256k1"
 
-	underlyingSecp256k1 "github.com/btcsuite/btcd/btcec"
+	underlyingSecp256k1 "github.com/tendermint/btcd/btcec"
 )
 
 type keyData struct {
```

### docs/architecture/adr-014-secp-malleability.md
```diff
@@ -47,7 +47,7 @@ Fork https://github.com/btcsuite/btcd, and just update the [parse sig method](ht
 
 ## Status
 
-Proposed.
+Implemented
 
 ## Consequences
 
```

### docs/architecture/adr-015-crypto-encoding.md
```diff
@@ -67,8 +67,7 @@ This is basically Ethereum's encoding, but without the leading recovery bit.
 
 ## Status
 
-Proposed. The signature section seems to be agreed upon for the most part.
-Needs decision on Enum types.
+Implemented
 
 ## Consequences
 
```
