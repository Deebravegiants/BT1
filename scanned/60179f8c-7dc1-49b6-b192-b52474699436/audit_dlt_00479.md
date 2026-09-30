# [?] trie/bintrie: fix overflow management in slot key computation (#33951)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-03-05
Source: https://github.com/ethereum/go-ethereum/commit/a0fb8102fefd524dcb1ad884f99ad310f7fe4fe2
Type: security-commit

## Details
trie/bintrie: fix overflow management in slot key computation (#33951)

The computation of `MAIN_STORAGE_OFFSET` was incorrect, causing the last
byte of the stem to be dropped. This means that there would be a
collision in the hash computation (at the preimage level, not a hash
collision of course) if two keys were only differing at byte 31.

## Patch
### core/genesis_test.go
```diff
@@ -308,7 +308,7 @@ func TestVerkleGenesisCommit(t *testing.T) {
 		},
 	}
 
-	expected := common.FromHex("b94812c1674dcf4f2bc98f4503d15f4cc674265135bcf3be6e4417b60881042a")
+	expected := common.FromHex("1fd154971d9a386c4ec75fe7138c17efb569bfc2962e46e94a376ba997e3fadc")
 	got := genesis.ToBlock().Root().Bytes()
 	if !bytes.Equal(got, expected) {
 		t.Fatalf("invalid genesis state root, expected %x, got %x", expected, got)
```

### trie/bintrie/key_encoding.go
```diff
@@ -47,13 +47,26 @@ var (
 )
 
 func GetBinaryTreeKey(addr common.Address, key []byte) []byte {
+	return getBinaryTreeKey(addr, key, false)
+}
+
+func getBinaryTreeKey(addr common.Address, offset []byte, overflow bool) []byte {
 	hasher := sha256.New()
 	hasher.Write(zeroHash[:12])
 	hasher.Write(addr[:])
-	hasher.Write(key[:31])
-	hasher.Write([]byte{0})
+	var buf [32]byte
+	// key is big endian, hashed value is little endian
+	for i := range offset[:31] {
+		buf[i] = offset[30-i]
+	}
+	if overflow {
+		// Overflow detected when adding MAIN_STORAGE_OFFSET,
+		// reporting it in the shifter 32 byte value.
+		buf[31] = 1
+	}
+	hasher.Write(buf[:])
 	k := hasher.Sum(nil)
-	k[31] = key[31]
+	k[31] = offset[31]
 	return k
 }
 
@@ -69,24 +82,29 @@ func GetBinaryTreeKeyCodeHash(addr common.Address) []byte {
 	return GetBinaryTreeKey(addr, k[:])
 }
 
-func GetBinaryTreeKeyStorageSlot(address common.Address, key []byte) []byte {
-	var k [32]byte
+func GetBinaryTreeKeyStorageSlot(address common.Address, slotnum []byte) []byte {
+	var offset [32]byte
 
 	// Case when the key belongs to the account header
-	if bytes.Equal(key[:31], zeroHash[:31]) && key[31] < 64 {
-		k[31] = 64 + key[31]
-		return GetBinaryTreeKey(address, k[:])
+	if bytes.Equal(slotnum[:31], zeroHash[:31]) && slotnum[31] < 64 {
+		offset[31] = 64 + slotnum[31]
+		return GetBinaryTreeKey(address, offset[:])
 	}
 
-	// Set the main storage offset
-	// note that the first 64 bytes of the main offset storage
-	// are unreachable, which is consistent with the spec and
-	// what verkle does.
-	k[0] = 1 // 1 << 248
-	copy(k[1:], key[:31])
-	k[31] = key[31]
-
-	return GetBinaryTreeKey(address, k[:])
+	// Set the main storage offset offset = MAIN_STORAGE_OFFSET + slotnum
+	//   * Note that MAIN_STORAGE_OFFSET is 1 << 248, so the number
+	//     can overflow into a 33rd byte, but since the value is
+	//     shifted by one byte in getBinaryTreeKey, this only takes
+	//     note of the overflow, and the value will be added after
+	//     the shift, in order to avoid allocating an extra byte.
+	//   * Note that the first 64 bytes of the main offset storage
+	//     are unreachable, which is consistent with the spec.
+	//   * Note that `slotnum` is big-endian
+	overflow := slotnum[0] == 255
+	copy(offset[:], slotnum)
+	offset[0] += 1 // 1 << 248, handle overflow out of band
+
+	return getBinaryTreeKey(address, offset[:], overflow)
 }
 
 func GetBinaryTreeKeyCodeChunk(address common.Address, chunknr *uint256.Int) []byte {
```
