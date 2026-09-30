# [?] Fix panic if terra keys remain in db (#8505)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-02-23
Source: https://github.com/smartcontractkit/ccip/commit/f69ef2009f879b4c1b80938de9eb6546d3b4e2ac
Type: security-commit

## Details
Fix panic if terra keys remain in db (#8505)

## Patch
### core/services/keystore/keys/ocr2key/key_bundle.go
```diff
@@ -106,7 +106,7 @@ func (raw Raw) Key() (kb KeyBundle) {
 	case chaintype.StarkNet:
 		kb = newKeyBundle(new(starknet.OCR2Key))
 	default:
-		panic(chaintype.NewErrInvalidChainType(temp.ChainType))
+		return nil
 	}
 	if err := kb.Unmarshal(raw); err != nil {
 		panic(err)
```

### core/services/keystore/legacy_key.go
```diff
@@ -0,0 +1,108 @@
+package keystore
+
+import (
+	"encoding/json"
+
+	"github.com/pkg/errors"
+)
+
+type rawLegacyKey []string
+type rawLegacyKeys map[string]rawLegacyKey
+
+type LegacyKeyStorage struct {
+	legacyRawKeys rawLegacyKeys
+}
+
+func (rlk *rawLegacyKeys) len() (n int) {
+	for _, v := range *rlk {
+		n += len(v)
+	}
+	return n
+}
+
+func (rlk *rawLegacyKeys) has(name string) bool {
+	for n := range *rlk {
+		if n == name {
+			return true
+		}
+	}
+	return false
+}
+
+func (rlk *rawLegacyKeys) hasValueInField(fieldName, value string) bool {
+	for _, v := range (*rlk)[fieldName] {
+		if v == value {
+			return true
+		}
+	}
+	return false
+}
+
+// StoreUnsupported will store the raw keys that no longer have support in the node
+// it will check if raw json contains keys that have not been added to the key ring
+// and stores them internally
+func (k *LegacyKeyStorage) StoreUnsupported(allRawKeysJson []byte, keyRing *keyRing) error {
+	if keyRing == nil {
+		return errors.New("keyring is nil")
+	}
+	supportedKeyRingJson, err := json.Marshal(keyRing.raw())
+	if err != nil {
+		return err
+	}
+
+	var (
+		allKeys       = rawLegacyKeys{}
+		supportedKeys = rawLegacyKeys{}
+	)
+
+	err = json.Unmarshal(allRawKeysJson, &allKeys)
+	if err != nil {
+		return err
+	}
+	err = json.Unmarshal(supportedKeyRingJson, &supportedKeys)
+	if err != nil {
+		return err
+	}
+
+	k.legacyRawKeys = rawLegacyKeys{}
+	for fName, fValue := range allKeys {
+		if !supportedKeys.has(fName) {
+			k.legacyRawKeys[fName] = fValue
+			continue
+		}
+		for _, v := range allKeys[fName] {
+			if !supportedKeys.hasValueInField(fName, v) {
+				k.legacyRawKeys[fName] = append(k.legacyRawKeys[fName], v)
+			}
+		}
+	}
+
+	return nil
+}
+
+// UnloadUnsupported will inject the unsupported keys into the raw key ring json
+func (k *LegacyKeyStorage) UnloadUnsupported(supportedRawKeyRingJson []byte) ([]byte, error) {
+	supportedKeys := rawLegacyKeys{}
+	err := json.Unmarshal(supportedRawKeyRingJson, &supportedKeys)
+	if err != nil {
+		return nil, err
+	}
+
+	for fName, vals := range k.legacyRawKeys {
+		if !supportedKeys.has(fName) {
+			supportedKeys[fName] = vals
+			continue
+		}
+		for _, v := range vals {
+			if !supportedKeys.hasValueInField(fName, v) {
+				supportedKeys[fName] = append(supportedKeys[fName], v)
+			}
+		}
+	}
+
+	allKeysJson, err := json.Marshal(supportedKeys)
+	if err != nil {
+		return nil, err
+	}
+	return allKeysJson, nil
+}
```

### core/services/keystore/master.go
```diff
@@ -7,6 +7,7 @@ import (
 	"sync"
 
 	starkkey "github.com/smartcontractkit/chainlink-starknet/relayer/pkg/chainlink/keys"
+
 	"github.com/smartcontractkit/chainlink/core/services/keystore/keys/dkgencryptkey"
 	"github.com/smartcontractkit/chainlink/core/services/keystore/keys/dkgsignkey"
 	"github.com/smartcontractkit/chainlink/core/services/keystore/keys/ocr2key"
```

### core/services/keystore/models.go
```diff
@@ -53,6 +53,13 @@ func (ekr encryptedKeyRing) Decrypt(password string) (*keyRing, error) {
 	if err != nil {
 		return nil, err
 	}
+
+	err = rawKeys.LegacyKeys.StoreUnsupported(marshalledRawKeyRingJson, ring)
+	if err != nil {
+		return nil, err
+	}
+	ring.LegacyKeys = rawKeys.LegacyKeys
+
 	return ring, nil
 }
 
@@ -145,6 +152,7 @@ type keyRing struct {
 	VRF        map[string]vrfkey.KeyV2
 	DKGSign    map[string]dkgsignkey.Key
 	DKGEncrypt map[string]dkgencryptkey.Key
+	LegacyKeys LegacyKeyStorage
 }
 
 func newKeyRing() *keyRing {
@@ -167,6 +175,12 @@ func (kr *keyRing) Encrypt(password string, scryptParams utils.ScryptParams) (ek
 	if err != nil {
 		return ekr, err
 	}
+
+	marshalledRawKeyRingJson, err = kr.LegacyKeys.UnloadUnsupported(marshalledRawKeyRingJson)
+	if err != nil {
+		return encryptedKeyRing{}, err
+	}
+
 	cryptoJSON, err := gethkeystore.EncryptDataV3(
 		marshalledRawKeyRingJson,
 		[]byte(adulteratedPassword(password)),
@@ -291,6 +305,9 @@ func (kr *keyRing) logPubKeys(lggr logger.Logger) {
 	if len(dkgEncryptIDs) > 0 {
 		lggr.Infow(fmt.Sprintf("Unlocked %d DKGEncrypt keys", len(dkgEncryptIDs)), "keys", dkgEncryptIDs)
 	}
+	if len(kr.LegacyKeys.legacyRawKeys) > 0 {
+		lggr.Infow(fmt.Sprintf("%d keys stored in legacy system", kr.LegacyKeys.legacyRawKeys.len()))
+	}
 }
 
 // rawKeyRing is an intermediate struct for encrypting / decrypting keyRing
@@ -307,6 +324,7 @@ type rawKeyRing struct {
 	VRF        []vrfkey.Raw
 	DKGSign    []dkgsignkey.Raw
 	DKGEncrypt []dkgencryptkey.Raw
+	LegacyKeys LegacyKeyStorage `json:"-"`
 }
 
 func (rawKeys rawKeyRing) keys() (*keyRing, error) {
@@ -324,8 +342,9 @@ func (rawKeys rawKeyRing) keys() (*keyRing, error) {
 		keyRing.OCR[ocrKey.ID()] = ocrKey
 	}
 	for _, rawOCR2Key := range rawKeys.OCR2 {
-		ocr2Key := rawOCR2Key.Key()
-		keyRing.OCR2[ocr2Key.ID()] = ocr2Key
+		if ocr2Key := rawOCR2Key.Key(); ocr2Key != nil {
+			keyRing.OCR2[ocr2Key.ID()] = ocr2Key
+		}
 	}
 	for _, rawP2PKey := range rawKeys.P2P {
 		p2pKey := rawP2PKey.Key()
@@ -351,6 +370,8 @@ func (rawKeys rawKeyRing) keys() (*keyRing, error) {
 		dkgEncryptKey := rawDKGEncryptKey.Key()
 		keyRing.DKGEncrypt[dkgEncryptKey.ID()] = dkgEncryptKey
 	}
+
+	keyRing.LegacyKeys = rawKeys.LegacyKeys
 	return keyRing, nil
 }
 
```

### core/services/keystore/models_test.go
```diff
@@ -2,6 +2,7 @@ package keystore
 
 import (
 	"crypto/rand"
+	"encoding/json"
 	"math/big"
 	"testing"
 
@@ -52,60 +53,112 @@ func TestKeyRing_Encrypt_Decrypt(t *testing.T) {
 		DKGSign:    []dkgsignkey.Raw{dkgsign1.Raw(), dkgsign2.Raw()},
 		DKGEncrypt: []dkgencryptkey.Raw{dkgencrypt1.Raw(), dkgencrypt2.Raw()},
 	}
-	originalKeyRing, err := originalKeyRingRaw.keys()
-	require.NoError(t, err)
+	originalKeyRing, kerr := originalKeyRingRaw.keys()
+	require.NoError(t, kerr)
+
+	t.Run("test encrypt/decrypt", func(t *testing.T) {
+		encryptedKr, err := originalKeyRing.Encrypt(password, utils.FastScryptParams)
+		require.NoError(t, err)
+		decryptedKeyRing, err := encryptedKr.Decrypt(password)
+		require.NoError(t, err)
+		// compare csa keys
+		require.Equal(t, 2, len(decryptedKeyRing.CSA))
+		require.Equal(t, originalKeyRing.CSA[csa1.ID()].PublicKey, decryptedKeyRing.CSA[csa1.ID()].PublicKey)
+		require.Equal(t, originalKeyRing.CSA[csa2.ID()].PublicKey, decryptedKeyRing.CSA[csa2.ID()].PublicKey)
+		// compare eth keys
+		require.Equal(t, 2, len(decryptedKeyRing.Eth))
+		require.Equal(t, originalKeyRing.Eth[eth1.ID()].Address, decryptedKeyRing.Eth[eth1.ID()].Address)
+		require.Equal(t, originalKeyRing.Eth[eth2.ID()].Address, decryptedKeyRing.Eth[eth2.ID()].Address)
+		// compare ocr keys
+		require.Equal(t, 2, len(decryptedKeyRing.OCR))
+		require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OnChainSigning.X, decryptedKeyRing.OCR[ocr[0].ID()].OnChainSigning.X)
+		require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OnChainSigning.Y, decryptedKeyRing.OCR[ocr[0].ID()].OnChainSigning.Y)
+		require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OnChainSigning.D, decryptedKeyRing.OCR[ocr[0].ID()].OnChainSigning.D)
+		require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OffChainSigning, decryptedKeyRing.OCR[ocr[0].ID()].OffChainSigning)
+		require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OffChainEncryption, decryptedKeyRing.OCR[ocr[0].ID()].OffChainEncryption)
+		require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OnChainSigning.X, decryptedKeyRing.OCR[ocr[1].ID()].OnChainSigning.X)
+		require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OnChainSigning.Y, decryptedKeyRing.OCR[ocr[1].ID()].OnChainSigning.Y)
+		require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OnChainSigning.D, decryptedKeyRing.OCR[ocr[1].ID()].OnChainSigning.D)
+		require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OffChainSigning, decryptedKeyRing.OCR[ocr[1].ID()].OffChainSigning)
+		require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OffChainEncryption, decryptedKeyRing.OCR[ocr[1].ID()].OffChainEncryption)
+		// compare ocr2 keys
+		require.Equal(t, len(chaintype.SupportedChainTypes), len(decryptedKeyRing.OCR2))
+		for i := range ocr2 {
+			id := ocr2[i].ID()
+			require.Equal(t, originalKeyRing.OCR2[id].ID(), decryptedKeyRing.OCR2[id].ID())
+			require.Equal(t, ocr2[i].OnChainPublicKey(), decryptedKeyRing.OCR2[id].OnChainPublicKey())
+			require.Equal(t, originalKeyRing.OCR2[id].ChainType(), decryptedKeyRing.OCR2[id].ChainType())
+		}
+		// compare p2p keys
+		require.Equal(t, 2, len(decryptedKeyRing.P2P))
+		require.Equal(t, originalKeyRing.P2P[p2p1.ID()].GetPublic(), decryptedKeyRing.P2P[p2p1.ID()].GetPublic())
+		require.Equal(t, originalKeyRing.P2P[p2p1.ID()].PeerID(), decryptedKeyRing.P2P[p2p1.ID()].PeerID())
+		require.Equal(t, originalKeyRing.P2P[p2p2.ID()].GetPublic(), decryptedKeyRing.P2P[p2p2.ID()].GetPublic())
+		require.Equal(t, originalKeyRing.P2P[p2p2.ID()].PeerID(), decryptedKeyRing.P2P[p2p2.ID()].PeerID())
+		// compare solana keys
+		require.Equal(t, 2, len(decryptedKeyRing.Solana))
+		require.Equal(t, originalKeyRing.Solana[sol1.ID()].GetPublic(), decryptedKeyRing.Solana[sol1.ID()].GetPublic())
+		// compare vrf keys
+		require.Equal(t, 2, len(decryptedKeyRing.VRF))
+		require.Equal(t, originalKeyRing.VRF[vrf1.ID()].PublicKey, decryptedKeyRing.VRF[vrf1.ID()].PublicKey)
+		require.Equal(t, originalKeyRing.VRF[vrf2.ID()].PublicKey, decryptedKeyRing.VRF[vrf2.ID()].PublicKey)
+		// compare dkgsign keys
+		require.Equal(t, 2, len(decryptedKeyRing.DKGSign))
+		require.Equal(t, originalKeyRing.DKGSign[dkgsign1.ID()].PublicKey, decryptedKeyRing.DKGSign[dkgsign1.ID()].PublicKey)
+		require.Equal(t, originalKeyRing.DKGSign[dkgsign2.ID()].PublicKey, decryptedKeyRing.DKGSign[dkgsign2.ID()].PublicKey)
+		// compare dkgencrypt keys
+		require.Equal(t, 2, len(decryptedKeyRing.DKGEncrypt))
+		require.Equal(t, originalKeyRing.DKGEncrypt[dkgencrypt1.ID()].PublicKey, decryptedKeyRing.DKGEncrypt[dkgencrypt1.ID()].PublicKey)
+		require.Equal(t, originalKeyRing.DKGEncrypt[dkgencrypt2.ID()].PublicKey, decryptedKeyRing.DKGEncrypt[dkgencrypt2.ID()].PublicKey)
+	})
+
+	t.Run("test legacy system", func(t *testing.T) {
+		//Add unsupported keys to raw json
+		rawJson, _ := json.Marshal(originalKeyRing.raw())
+		var allKeys = map[string][]string{
+			"foo": {
+				"bar", "biz",
+			},
+		}
+		err := json.Unmarshal(rawJson, &allKeys)
+		require.NoError(t, err)
+		//Add more ocr2 keys
+		newOCR2Key1 := ocrkey.MustNewV2XXXTestingOnly(big.NewInt(5))
+		newOCR2Key2 := ocrkey.MustNewV2XXXTestingOnly(big.NewInt(6))
+		allKeys["OCR2"] = append(allKeys["OCR2"], newOCR2Key1.Raw().String())
+		allKeys["OCR2"] = append(allKeys["OCR2"], newOCR2Key2.Raw().String())
+
+		//Add more p2p keys
+		newP2PKey1 := p2pkey.MustNewV2XXXTestingOnly(big.NewInt(5))
+		newP2PKey2 := p2pkey.MustNewV2XXXTestingOnly(big.NewInt(7))
+		allKeys["P2P"] = append(allKeys["P2P"], newP2PKey1.Raw().String())
+		allKeys["P2P"] = append(allKeys["P2P"], newP2PKey2.Raw().String())
+
+		//Run legacy system
+		newRawJson, _ := json.Marshal(allKeys)
+		err = originalKeyRing.LegacyKeys.StoreUnsupported(newRawJson, originalKeyRing)
+		require.NoError(t, err)
+		require.Equal(t, originalKeyRing.LegacyKeys.legacyRawKeys.len(), 6)
+		marshalledRawKeyRingJson, err := json.Marshal(originalKeyRing.raw())
+		require.NoError(t, err)
+		unloadedKeysJson, err := originalKeyRing.LegacyKeys.UnloadUnsupported(marshalledRawKeyRingJson)
+		require.NoError(t, err)
+		var shouldHaveAllKeys = map[string][]string{}
+		err = json.Unmarshal(unloadedKeysJson, &shouldHaveAllKeys)
+		require.NoError(t, err)
+
+		//Check if keys where added to the raw json
+		require.Equal(t, shouldHaveAllKeys["foo"], []string{"bar", "biz"})
+		require.Contains(t, shouldHaveAllKeys["OCR2"], newOCR2Key1.Raw().String())
+		require.Contains(t, shouldHaveAllKeys["OCR2"], newOCR2Key2.Raw().String())
+		require.Contains(t, shouldHaveAllKeys["P2P"], newP2PKey1.Raw().String())
+		require.Contains(t, shouldHaveAllKeys["P2P"], newP2PKey2.Raw().String())
+
+		//Check error
+		err = originalKeyRing.LegacyKeys.StoreUnsupported(newRawJson, nil)
+		require.Error(t, err)
+		_, err = originalKeyRing.LegacyKeys.UnloadUnsupported(nil)
+		require.Error(t, err)
+	})
 
-	encryptedKeyRing, err := originalKeyRing.Encrypt(password, utils.FastScryptParams)
-	require.NoError(t, err)
-	decryptedKeyRing, err := encryptedKeyRing.Decrypt(password)
-	require.NoError(t, err)
-	// compare csa keys
-	require.Equal(t, 2, len(decryptedKeyRing.CSA))
-	require.Equal(t, originalKeyRing.CSA[csa1.ID()].PublicKey, decryptedKeyRing.CSA[csa1.ID()].PublicKey)
-	require.Equal(t, originalKeyRing.CSA[csa2.ID()].PublicKey, decryptedKeyRing.CSA[csa2.ID()].PublicKey)
-	// compare eth keys
-	require.Equal(t, 2, len(decryptedKeyRing.Eth))
-	require.Equal(t, originalKeyRing.Eth[eth1.ID()].Address, decryptedKeyRing.Eth[eth1.ID()].Address)
-	require.Equal(t, originalKeyRing.Eth[eth2.ID()].Address, decryptedKeyRing.Eth[eth2.ID()].Address)
-	// compare ocr keys
-	require.Equal(t, 2, len(decryptedKeyRing.OCR))
-	require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OnChainSigning.X, decryptedKeyRing.OCR[ocr[0].ID()].OnChainSigning.X)
-	require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OnChainSigning.Y, decryptedKeyRing.OCR[ocr[0].ID()].OnChainSigning.Y)
-	require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OnChainSigning.D, decryptedKeyRing.OCR[ocr[0].ID()].OnChainSigning.D)
-	require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OffChainSigning, decryptedKeyRing.OCR[ocr[0].ID()].OffChainSigning)
-	require.Equal(t, originalKeyRing.OCR[ocr[0].ID()].OffChainEncryption, decryptedKeyRing.OCR[ocr[0].ID()].OffChainEncryption)
-	require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OnChainSigning.X, decryptedKeyRing.OCR[ocr[1].ID()].OnChainSigning.X)
-	require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OnChainSigning.Y, decryptedKeyRing.OCR[ocr[1].ID()].OnChainSigning.Y)
-	require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OnChainSigning.D, decryptedKeyRing.OCR[ocr[1].ID()].OnChainSigning.D)
-	require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OffChainSigning, decryptedKeyRing.OCR[ocr[1].ID()].OffChainSigning)
-	require.Equal(t, originalKeyRing.OCR[ocr[1].ID()].OffChainEncryption, decryptedKeyRing.OCR[ocr[1].ID()].OffChainEncryption)
-	// compare ocr2 keys
-	require.Equal(t, len(chaintype.SupportedChainTypes), len(decryptedKeyRing.OCR2))
-	for i := range ocr2 {
-		id := ocr2[i].ID()
-		require.Equal(t, originalKeyRing.OCR2[id].ID(), decryptedKeyRing.OCR2[id].ID())
-		require.Equal(t, ocr2[i].OnChainPublicKey(), decryptedKeyRing.OCR2[id].OnChainPublicKey())
-		require.Equal(t, originalKeyRing.OCR2[id].ChainType(), decryptedKeyRing.OCR2[id].ChainType())
-	}
-	// compare p2p keys
-	require.Equal(t, 2, len(decryptedKeyRing.P2P))
-	require.Equal(t, originalKeyRing.P2P[p2p1.ID()].GetPublic(), decryptedKeyRing.P2P[p2p1.ID()].GetPublic())
-	require.Equal(t, originalKeyRing.P2P[p2p1.ID()].PeerID(), decryptedKeyRing.P2P[p2p1.ID()].PeerID())
-	require.Equal(t, originalKeyRing.P2P[p2p2.ID()].GetPublic(), decryptedKeyRing.P2P[p2p2.ID()].GetPublic())
-	require.Equal(t, originalKeyRing.P2P[p2p2.ID()].PeerID(), decryptedKeyRing.P2P[p2p2.ID()].PeerID())
-	// compare solana keys
-	require.Equal(t, 2, len(decryptedKeyRing.Solana))
-	require.Equal(t, originalKeyRing.Solana[sol1.ID()].GetPublic(), decryptedKeyRing.Solana[sol1.ID()].GetPublic())
-	// compare vrf keys
-	require.Equal(t, 2, len(decryptedKeyRing.VRF))
-	require.Equal(t, originalKeyRing.VRF[vrf1.ID()].PublicKey, decryptedKeyRing.VRF[vrf1.ID()].PublicKey)
-	require.Equal(t, originalKeyRing.VRF[vrf2.ID()].PublicKey, decryptedKeyRing.VRF[vrf2.ID()].PublicKey)
-	// compare dkgsign keys
-	require.Equal(t, 2, len(decryptedKeyRing.DKGSign))
-	require.Equal(t, originalKeyRing.DKGSign[dkgsign1.ID()].PublicKey, decryptedKeyRing.DKGSign[dkgsign1.ID()].PublicKey)
-	require.Equal(t, originalKeyRing.DKGSign[dkgsign2.ID()].PublicKey, decryptedKeyRing.DKGSign[dkgsign2.ID()].PublicKey)
-	// compare dkgencrypt keys
-	require.Equal(t, 2, len(decryptedKeyRing.DKGEncrypt))
-	require.Equal(t, originalKeyRing.DKGEncrypt[dkgencrypt1.ID()].PublicKey, decryptedKeyRing.DKGEncrypt[dkgencrypt1.ID()].PublicKey)
-	require.Equal(t, originalKeyRing.DKGEncrypt[dkgencrypt2.ID()].PublicKey, decryptedKeyRing.DKGEncrypt[dkgencrypt2.ID()].PublicKey)
 }
```
