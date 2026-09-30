# [?] Merge pull request #2374 from ffranr/2372-fix-bip32-derivation-overflow-bug

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2025-06-06
Source: https://github.com/btcsuite/btcd/commit/0cba26df01951cee426074eaa53eed654249c3a4
Type: security-commit

## Details
Merge pull request #2374 from ffranr/2372-fix-bip32-derivation-overflow-bug

psbt: overflow checks when computing Taproot BIP32 derivation min size

## Patch
### btcutil/psbt/psbt_test.go
```diff
@@ -9,6 +9,7 @@ import (
 	"encoding/base64"
 	"encoding/binary"
 	"encoding/hex"
+	"math"
 	"strings"
 	"testing"
 
@@ -1447,6 +1448,89 @@ func TestNonWitnessToWitness(t *testing.T) {
 	}
 }
 
+// TestPSBTNumberOfHashesOverflow tests the case where the number of hashes
+// in the PSBT exceeds the maximum allowed value. This is a regression test
+// for a bug that was fixed in the PSBT library.
+func TestPSBTNumberOfHashesOverflow(t *testing.T) {
+	// This hex string represents a PSBT with an invalid number of hashes. The
+	// PSBT library should return an error when trying to parse this PSBT.
+	//
+	// TODO(ffranr): Is there a more minimal PSBT example?
+	hexString := "70736274ff01007374ff01030100000000002f0000002e2873007374" +
+		"ff01070100000000000000000000000000000000000000060680050000736274f" +
+		"f01000a0000000060c70006060000736274ff01000a0000010000010024070100" +
+		"00000000000000000000000000000000000006060000736274ff01000a0000000" +
+		"000010024c760002a707362c760000b0500000000000000060605000073626274" +
+		"ff01000a000000000001002421212121212121212121212121212121212121212" +
+		"12121212121212121212121212121212107010000000000000000000000000000" +
+		"000000000006060000736274ff01000a000eff000001000a0a040404040404040" +
+		"400"
+
+	// Convert hex string to byte slice
+	buffer, err := hex.DecodeString(hexString)
+	require.NoError(t, err)
+
+	// Attempt to parse the PSBT.
+	psbt, err := NewFromRawBytes(bytes.NewBuffer(buffer), false)
+	require.Nil(t, psbt)
+	require.ErrorIs(t, err, ErrInvalidPsbtFormat)
+}
+
+// TestMinTaprootBip32DerivationByteSize tests the
+// minTaprootBip32DerivationByteSize function to ensure it correctly calculates
+// the minimum byte size of the Taproot BIP32 derivation path.
+func TestMinTaprootBip32DerivationByteSize(t *testing.T) {
+	tests := []struct {
+		label        string
+		numHashes    uint64
+		expectedSize uint64
+		expectErr    bool
+	}{
+		{
+			label:        "only compact size + fingerprint",
+			numHashes:    0,
+			expectedSize: 5,
+			expectErr:    false,
+		},
+		{
+			label:        "numHashes == 1, therefore: 1 * 32 + 5",
+			numHashes:    1,
+			expectedSize: 37,
+			expectErr:    false,
+		},
+		{
+			label:        "numHashes == 2, therefore: 2 * 32 + 5",
+			numHashes:    2,
+			expectedSize: 69,
+			expectErr:    false,
+		},
+		{
+			label:        "overflow expected",
+			numHashes:    math.MaxUint64,
+			expectedSize: 0,
+			expectErr:    true,
+		},
+	}
+
+	for _, tt := range tests {
+		actualSize, err := minTaprootBip32DerivationByteSize(tt.numHashes)
+
+		if (err != nil) != tt.expectErr {
+			t.Errorf(
+				"%s (numHashes=%d, unexpected_error=%v)", tt.label,
+				tt.numHashes, err,
+			)
+			continue
+		}
+
+		if err == nil && actualSize != tt.expectedSize {
+			t.Errorf("%s (numHashes=%d, actualSize=%d, expectedSize=%d)",
+				tt.label, tt.numHashes, actualSize, tt.expectedSize,
+			)
+		}
+	}
+}
+
 // TestEmptyInputSerialization tests the special serialization case for a wire
 // transaction that has no inputs.
 func TestEmptyInputSerialization(t *testing.T) {
```

### btcutil/psbt/taproot.go
```diff
@@ -2,6 +2,8 @@ package psbt
 
 import (
 	"bytes"
+	"math"
+	"math/bits"
 
 	"github.com/btcsuite/btcd/btcec/v2/schnorr"
 	"github.com/btcsuite/btcd/txscript"
@@ -93,12 +95,61 @@ func (s *TaprootBip32Derivation) SortBefore(other *TaprootBip32Derivation) bool
 	return bytes.Compare(s.XOnlyPubKey, other.XOnlyPubKey) < 0
 }
 
+// minTaprootBip32DerivationByteSize returns the minimum number of bytes
+// required to encode a Taproot BIP32 derivation field, given the number of
+// leaf hashes.
+//
+// NOTE: This function does not account for the size of the BIP32 child indexes,
+// as we are only computing the minimum size (which occurs when the path is
+// empty). The bits package is used to safely detect and handle overflows.
+func minTaprootBip32DerivationByteSize(numHashes uint64) (uint64, error) {
+	// The Taproot BIP32 derivation field is encoded as:
+	//   [compact size uint: number of leaf hashes]
+	//   [N × 32 bytes: leaf hashes]
+	//   [4 bytes: master key fingerprint]
+	//   [M × 4 bytes: BIP32 child indexes]
+	//
+	// To compute the minimum size given the number of hashes only, we assume:
+	// - N = numHashes (provided)
+	// - M = 0 (no child indexes)
+	//
+	// So the base byte size is:
+	//   1 (leaf hash count) + (N × 32) + 4 (fingerprint)
+	//
+	// First, we calculate the total number of bytes for the leaf hashes.
+	mulCarry, totalHashesBytes := bits.Mul64(numHashes, 32)
+	if mulCarry != 0 {
+		return 0, ErrInvalidPsbtFormat
+	}
+
+	// Since we're computing the minimum possible size, we add a constant that
+	// accounts for the fixed size fields:
+	// * 1 byte for the compact size leaf hash count (assumes numHashes < 0xfd)
+	// * 4 bytes for the master key fingerprint
+	// Total: 5 bytes.
+	// All other fields (e.g., BIP32 path) are assumed absent for minimum size
+	// calculation.
+	result, addCarry := bits.Add64(5, totalHashesBytes, 0)
+	if addCarry != 0 {
+		return 0, ErrInvalidPsbtFormat
+	}
+
+	return result, nil
+}
+
 // ReadTaprootBip32Derivation deserializes a byte slice containing the Taproot
 // BIP32 derivation info that consists of a list of leaf hashes as well as the
 // normal BIP32 derivation info.
 func ReadTaprootBip32Derivation(xOnlyPubKey,
 	value []byte) (*TaprootBip32Derivation, error) {
 
+	// This function allocates additional memory while parsing the serialized
+	// data. To prevent potential out-of-memory (OOM) issues, we must validate
+	// the length of the value slice before proceeding.
+	if len(value) > MaxPsbtValueLength {
+		return nil, ErrInvalidPsbtFormat
+	}
+
 	// The taproot key BIP 32 derivation path is defined as:
 	//   <hashes len> <leaf hash>* <4 byte fingerprint> <32-bit uint>*
 	// So we get at least 5 bytes for the length and the 4 byte fingerprint.
@@ -113,9 +164,22 @@ func ReadTaprootBip32Derivation(xOnlyPubKey,
 		return nil, ErrInvalidPsbtFormat
 	}
 
-	// A hash is 32 bytes in size, so we need at least numHashes*32 + 5
-	// bytes to be present.
-	if len(value) < (int(numHashes)*32)+5 {
+	// As a safety/sanity check, verify that the hash count fits in a `uint32`.
+	// This isn’t mandated by BIP‑371, but it prevents overflow and limits
+	// derivations to about 137 GiB of data.
+	if numHashes > math.MaxUint32 {
+		return nil, ErrInvalidPsbtFormat
+	}
+
+	// Given the number of hashes, we can calculate the minimum byte size
+	// of the taproot BIP32 derivation.
+	minByteSize, err := minTaprootBip32DerivationByteSize(numHashes)
+	if err != nil {
+		return nil, err
+	}
+
+	// Ensure that value is at least the minimum size.
+	if uint64(len(value)) < minByteSize {
 		return nil, ErrInvalidPsbtFormat
 	}
 
```
