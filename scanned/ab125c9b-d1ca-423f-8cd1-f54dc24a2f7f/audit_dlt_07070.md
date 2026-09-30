# [?] GenerateWitness: Fix panic during unfold (#18942)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-02-03
Source: https://github.com/erigontech/erigon/commit/645736e4d600f912e038485f4f2e7e1a89790efc
Type: security-commit

## Details
GenerateWitness: Fix panic during unfold (#18942)

This unit test reproduces a panic I've encountered when requesting trie
witness for an account and storage slot of another account in one batch
(i.e. in one call to `GenerateWitness`.

`MultiKeyWitness_AccountWithSingletonStorage` fails with:

```
panic: runtime error: index out of range [16] with length 16 [recovered]
	panic: runtime error: index out of range [16] with length 16
```

This happens during the unfold of the storage key, and I think the
reason is that the fold didn't happen correctly before that.

The full trace is :

```
go test -test.fullpath=true -timeout 600s -run ^Test_WitnessTrie_GenerateWitness$/^MultiKeyWitness_AccountWithSingletonStorage$ github.com/erigontech/erigon/execution/commitment

addr (prefix 0x5) 709b0758083f61d375bc02b41df4f91929e18fda
addr (prefix 0xa) 6b6fed27ff8974bac0cafd9ad05692b13619e738
storage 964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb -> 964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb
(1/3) plainKey [709b0758083f61d375bc02b41df4f91929e18fda] Flags: [+Balance], Balance: [100] hashedKey [050804010901090c090308080c0d0f07080e0e00010507070c03040a0d0c050609010d00080008090f0701040501060f0701010a0a02000c01000b0300000c07] currentKey []
needUnfolding root, rootChecked = false
unfold 1: activeRows: 0
unfold root: touched: false present: false {loaded=false}
unfoldBranchNode prefix '00', nibbles [] depth 1 row 0 ''
needUnfolding root, rootChecked = true
set downHasheKey=[050804010901090c090308080c0d0f07080e0e00010507070c03040a0d0c050609010d00080008090f0701040501060f0701010a0a02000c01000b0300000c07]
updateCell 709b0758083f61d375bc02b41df4f91929e18fda => Flags: [+Balance], Balance: [100]
(2/3) plainKey [6b6fed27ff8974bac0cafd9ad05692b13619e738] Flags: [+Balance], Balance: [200] hashedKey [0a0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f02040308] currentKey []
needUnfolding root, rootChecked = true
cpl=0 cell.hashedExtension=[050804010901090c090308080c0d0f07080e0e00010507070c03040a0d0c050609010d00080008090f0701040501060f0701010a0a02000c01000b0300000c07] hashedKey[depth=0:]=[0a0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f02040308]
unfold 1: activeRows: 0
unfold root: touched: true present: true {loaded=Account  addr=709b0758083f61d375bc02b41df4f91929e18fda balance=100 nonce=0 codeHash=EMPTY hashedExtension=050804010901090c090308080c0d0f07080e0e00010507070c03040a0d0c050609010d00080008090f0701040501060f0701010a0a02000c01000b0300000c07}
unfolded cell (0, 5, depth=1) {loaded=Account  addr=709b0758083f61d375bc02b41df4f91929e18fda balance=100 nonce=0 codeHash=EMPTY hashedExtension=0804010901090c090308080c0d0f07080e0e00010507070c03040a0d0c050609010d00080008090f0701040501060f0701010a0a02000c01000b0300000c07}
currentKey [] needUnfolding cell (0, a, depth=1) cell.hash=[]
updateCell setting (0, a, depth=1)
set downHasheKey=[0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f02040308]
updateCell 6b6fed27ff8974bac0cafd9ad05692b13619e738 => Flags: [+Balance], Balance: [200]
(3/3) plainKey [6b6fed27ff8974bac0cafd9ad05692b13619e738964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb] Flags: [+Storage], Storage: [964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb] hashedKey [0a0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f0204030803050d060e08030509010b060708010d0a0b060309060d010d00070305080703000a06070e000a0b0a0c080e0305040103030e060f0d08080d0f010c000d0305] currentKey []
currentKey [] needUnfolding cell (0, a, depth=1) cell.hash=[]
cpl=62 cell.hashedExtension=[0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f02040308] hashedKey[depth=1:]=[0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f0204030803050d060e08030509010b060708010d0a0b060309060d010d00070305080703000a06070e000a0b0a0c080e0305040103030e060f0d08080d0f010c000d0305]
unfold 63: activeRows: 1
upCell (0, a, updepth=1) touched: true present: true
unfolded cell (1, 8, depth=64) {loaded=Account  addr=6b6fed27ff8974bac0cafd9ad05692b13619e738 balance=200 nonce=0 codeHash=EMPTY}
currentKey [0a0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f020403] needUnfolding cell (1, 8, depth=64) cell.hash=[]
updateCell setting (1, 8, depth=64)
set downHasheKey=[03050d060e08030509010b060708010d0a0b060309060d010d00070305080703000a06070e000a0b0a0c080e0305040103030e060f0d08080d0f010c000d0305]
updateCell 6b6fed27ff8974bac0cafd9ad05692b13619e738964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb => Flags: [+Storage], Storage: [964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb]
fold [0a0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f020403] activeRows: 2 touchMap: 0000000100000000 afterMap: 0000000100000000
fold: parent (0, a, depth=1)
fold: (row=1, {8}, depth=64) prefix [0a0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f020403] touchMap: 0000000100000000 afterMap: 0000000100000000 
formed leaf (1 8, depth=64) [1a196bb56b96a66a835b2d1563c2d3cf630905829dd8f0778a89b261ede7f243] {loaded=Account Storage  addr=6b6fed27ff8974bac0cafd9ad05692b13619e738 balance=200 nonce=0 codeHash=EMPTY addr[s]=6b6fed27ff8974bac0cafd9ad05692b13619e738964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb storage=964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb hashedExtension=03050d060e08030509010b060708010d0a0b060309060d010d00070305080703000a06070e000a0b0a0c080e0305040103030e060f0d08080d0f010c000d0305}
fold [] activeRows: 1 touchMap: 0000010000100000 afterMap: 0000010000100000
fold: parent is root {loaded=Account  addr=709b0758083f61d375bc02b41df4f91929e18fda balance=100 nonce=0 codeHash=EMPTY hashedExtension=050804010901090c090308080c0d0f07080e0e00010507070c03040a0d0c050609010d00080008090f0701040501060f0701010a0a02000c01000b0300000c07}
fold: (row=0, {5,A}, depth=1) prefix [] touchMap: 0000010000100000 afterMap: 0000010000100000 
accountLeafHashWithKey {a0a7a0052a6938344bebbcb671fc857203d28cd97390aa38d826e7bc2c9aed4d9f} (memorised) for [0804010901090c090308080c0d0f07080e0e00010507070c03040a0d0c050609010d00080008090f0701040501060f0701010a0a02000c01000b0300000c0710]=>[f8448064a056e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421a0c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470]
leafHashWithKeyVal(singleton=true) {a0d3385607f70e0ad68d89bd41c7acb5f5cfc91ad6cf158b4a792fbaf412ac4bb2} for [03050d060e08030509010b060708010d0a0b060309060d010d00070305080703000a06070e000a0b0a0c080e0305040103030e060f0d08080d0f010c000d030510]=>[964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb] (hashedExtension(len=63)=03050d060e08030509010b060708010d0a0b060309060d010d00070305080703000a06070e000a0b0a0c080e0305040103030e060f0d08080d0f010c000d03, accountAddr=6b6fed27ff8974bac0cafd9ad05692b13619e738, storageAddr=6b6fed27ff8974bac0cafd9ad05692b13619e738964dfdc79e8d534373661cfd66d74fec1e1b89491ab7236e4b75216290cf2beb, )
accountLeafHashWithKey {a09ecd89e2b87e3a640e3ef846b204cb2afb0c93912702824b2f06322691c34df6} (memorised) for [0109060b0b05060b09060a06060a0803050b020d010506030c020d030c0f0603000900050802090d0d080f000707080a08090b0206010e0d0e070f0204030810]=>[f8458081c8a0d3385607f70e0ad68d89bd41c7acb5f5cfc91ad6cf158b4a792fbaf412ac4bb2a0c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470]
} [3a242aefe2cea9cfb59d87890c905bbd31ef058f95ac671c214ae9dd4d739c93]
root hash 3a242aefe2cea9cfb59d87890c905bbd31ef058f95ac671c214ae9dd4d739c93 updates 3
--- FAIL: Test_WitnessTrie_GenerateWitness (0.00s)
    --- FAIL: Test_WitnessTrie_GenerateWitness/MultiKeyWitness_AccountWithSingletonStorage (0.00s)
        /Users/user/Documents/repos/erigontech/erigon-support/execution/commitment/hex_patricia_hashed_test.go:2442: MultiKeyWitness_AccountWithSingletonStorage
panic: runtime error: index out of range [16] with length 16 [recovered]
	panic: runtime error: index out of range [16] with length 16

goroutine 36 [running]:
testing.tRunner.func1.2({0x100fcc7a0, 0x1400022a1b0})
	/opt/homebrew/Cellar/go/1.24.2/libexec/src/testing/testing.go:1734 +0x1ac
testing.tRunner.func1()
	/opt/homebrew/Cellar/go/1.24.2/libexec/src/testing/testing.go:1737 +0x334
panic({0x100fcc7a0?, 0x1400022a1b0?})
	/opt/homebrew/Cellar/go/1.24.2/libexec/src/runtime/panic.go:792 +0x124
github.com/erigontech/erigon/execution/commitment.(*HexPatriciaHashed).unfold(0x14000300000, {0x14000290080?, 0x80?, 0x80?}, 0x1)
	/Users/user/Documents/repos/erigontech/erigon-support/execution/commitment/hex_patricia_hashed.go:1812 +0x738
github.com/erigontech/erigon/execution/commitment.(*HexPatriciaHashed).GenerateWitness.func1({0x14000290080, 0x80, 0x80}, {0x140002501c0, 0x34, 0x34}, 0x0?)
	/Users/user/Documents/repos/erigontech/erigon-support/execution/commitment/hex_patricia_hashed.go:2479 +0x740
github.com/erigontech/erigon/execution/commitment.(*Updates).HashSort(0x1400013e240, {0x1010201d8, 0x1014bd0a0}, 0x0, 0x140000d4060)
	/Users/user/Documents/repos/erigontech/erigon-support/execution/commitment/commitment.go:1724 +0x314
github.com/erigontech/erigon/execution/commitment.(*HexPatriciaHashed).GenerateWitness(0x14000300000, {0x1010201d8, 0x1014bd0a0}, 0x1400013e240, 0x0, {0x0, 0x0})
	/Users/user/Documents/repos/erigontech/erigon-support/execution/commitment/hex_patricia_hashed.go:2436 +0x25c
github.com/erigontech/erigon/execution/commitment.Test_WitnessTrie_GenerateWitness.func1(0x14000256540, 0x14000149668, {0x1400003bf28, 0x2, 0x14000149628?}, {0x1400003b57e, 0x2, 0x0?})
	/Users/user/Documents/repos/erigontech/erigon-support/execution/commitment/hex_patricia_hashed_test.go:2038 +0x3b8
github.com/erigontech/erigon/execution/commitment.Test_WitnessTrie_GenerateWitness.func16(0x14000256540)
	/Users/user/Documents/repos/erigontech/erigon-support/execution/commitment/hex_patricia_hashed_test.go:2473 +0x97c
testing.tRunner(0x14000256540, 0x14000209c40)
	/opt/homebrew/Cellar/go/1.24.2/libexec/src/testing/testing.go:1792 +0xe4
created by testing.(*T).Run in goroutine 35
	/opt/homebrew/Cellar/go/1.24.2/libexec/src/testing/testing.go:1851 +0x374
FAIL	github.com/erigontech/erigon/execution/commitment	0.284s
FAIL
```

---------

Co-authored-by: antonis19 <antonis19@users.noreply.github.com>

## Patch
### execution/commitment/hex_patricia_hashed.go
```diff
@@ -867,6 +867,12 @@ func (hph *HexPatriciaHashed) witnessComputeCellHashWithStorage(cell *cell, dept
 	if hph.memoizationOff {
 		cell.stateHashLen = 0 // Reset stateHashLen to force recompute
 	}
+
+	// Use a temporary buffer for hashed key computation to avoid corrupting cell.hashedExtension
+	// which may be needed for subsequent witness operations on other keys
+	// note that the cell.hashedExtension overwrite is still present in the `computeCellHash()`
+	var hashedKeyBuf [128]byte
+
 	if cell.storageAddrLen > 0 {
 		var hashedKeyOffset int16
 		if depth >= 64 {
@@ -878,10 +884,10 @@ func (hph *HexPatriciaHashed) witnessComputeCellHashWithStorage(cell *cell, dept
 			// if account key is empty, then we need to hash storage key from the key beginning
 			koffset = 0
 		}
-		if err = hashKey(hph.keccak, cell.storageAddr[koffset:cell.storageAddrLen], cell.hashedExtension[:], hashedKeyOffset, cell.hashBuf[:]); err != nil {
+		if err = hashKey(hph.keccak, cell.storageAddr[koffset:cell.storageAddrLen], hashedKeyBuf[:], hashedKeyOffset, cell.hashBuf[:]); err != nil {
 			return nil, storageRootHashIsSet, nil, err
 		}
-		cell.hashedExtension[64-hashedKeyOffset] = terminatorHexByte // Add terminator
+		hashedKeyBuf[64-hashedKeyOffset] = terminatorHexByte // Add terminator
 
 		if cell.stateHashLen > 0 {
 			res := append([]byte{160}, cell.stateHash[:cell.stateHashLen]...)
@@ -913,10 +919,10 @@ func (hph *HexPatriciaHashed) witnessComputeCellHashWithStorage(cell *cell, dept
 			}
 			if singleton {
 				if hph.trace {
-					fmt.Printf("leafHashWithKeyVal(singleton) for [%x]=>[%x]\n", cell.hashedExtension[:64-hashedKeyOffset+1], cell.Storage[:cell.StorageLen])
+					fmt.Printf("leafHashWithKeyVal(singleton) for [%x]=>[%x]\n", hashedKeyBuf[:64-hashedKeyOffset+1], cell.Storage[:cell.StorageLen])
 				}
 				aux := hph.hashAuxBuffer[:0]
-				if aux, err = hph.leafHashWithKeyVal(aux, cell.hashedExtension[:64-hashedKeyOffset+1], cell.Storage[:cell.StorageLen], true); err != nil {
+				if aux, err = hph.leafHashWithKeyVal(aux, hashedKeyBuf[:64-hashedKeyOffset+1], cell.Storage[:cell.StorageLen], true); err != nil {
 					return nil, storageRootHashIsSet, nil, err
 				}
 				if hph.trace {
@@ -928,9 +934,9 @@ func (hph *HexPatriciaHashed) witnessComputeCellHashWithStorage(cell *cell, dept
 				hadToReset.Add(1)
 			} else {
 				if hph.trace {
-					fmt.Printf("leafHashWithKeyVal for [%x]=>[%x] %v\n", cell.hashedExtension[:64-hashedKeyOffset+1], cell.Storage[:cell.StorageLen], cell.String())
+					fmt.Printf("leafHashWithKeyVal for [%x]=>[%x] %v\n", hashedKeyBuf[:64-hashedKeyOffset+1], cell.Storage[:cell.StorageLen], cell.String())
 				}
-				leafHash, err := hph.leafHashWithKeyVal(buf, cell.hashedExtension[:64-hashedKeyOffset+1], cell.Storage[:cell.StorageLen], false)
+				leafHash, err := hph.leafHashWithKeyVal(buf, hashedKeyBuf[:64-hashedKeyOffset+1], cell.Storage[:cell.StorageLen], false)
 				if err != nil {
 					return nil, storageRootHashIsSet, nil, err
 				}
@@ -946,10 +952,10 @@ func (hph *HexPatriciaHashed) witnessComputeCellHashWithStorage(cell *cell, dept
 		}
 	}
 	if cell.accountAddrLen > 0 {
-		if err := hashKey(hph.keccak, cell.accountAddr[:cell.accountAddrLen], cell.hashedExtension[:], depth, cell.hashBuf[:]); err != nil {
+		if err := hashKey(hph.keccak, cell.accountAddr[:cell.accountAddrLen], hashedKeyBuf[:], depth, cell.hashBuf[:]); err != nil {
 			return nil, storageRootHashIsSet, nil, err
 		}
-		cell.hashedExtension[64-depth] = terminatorHexByte // Add terminator
+		hashedKeyBuf[64-depth] = terminatorHexByte // Add terminator
 		if !storageRootHashIsSet {
 			if cell.extLen > 0 { // Extension
 				if cell.hashLen == 0 {
@@ -998,9 +1004,9 @@ func (hph *HexPatriciaHashed) witnessComputeCellHashWithStorage(cell *cell, dept
 		var valBuf [128]byte
 		valLen := cell.accountForHashing(valBuf[:], storageRootHash)
 		if hph.trace {
-			fmt.Printf("accountLeafHashWithKey for [%x]=>[%x]\n", cell.hashedExtension[:65-depth], rlp.RlpEncodedBytes(valBuf[:valLen]))
+			fmt.Printf("accountLeafHashWithKey for [%x]=>[%x]\n", hashedKeyBuf[:65-depth], rlp.RlpEncodedBytes(valBuf[:valLen]))
 		}
-		leafHash, err := hph.accountLeafHashWithKey(buf, cell.hashedExtension[:65-depth], rlp.RlpEncodedBytes(valBuf[:valLen]))
+		leafHash, err := hph.accountLeafHashWithKey(buf, hashedKeyBuf[:65-depth], rlp.RlpEncodedBytes(valBuf[:valLen]))
 		if err != nil {
 			return nil, storageRootHashIsSet, nil, err
 		}
```

### execution/commitment/hex_patricia_hashed_test.go
```diff
@@ -2005,8 +2005,9 @@ func sortUpdatesByHashIncrease(t *testing.T, hph *HexPatriciaHashed, plainKeys [
 func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 	// t.Parallel()
 
-	buildTrieAndWitness := func(t *testing.T, builder *UpdateBuilder, plainKeyToWitness []byte, keyExists bool) {
+	buildTrieAndWitness := func(t *testing.T, builder *UpdateBuilder, plainKeysToWitness [][]byte, keyExists []bool) {
 		t.Helper()
+		require.Equal(t, len(plainKeysToWitness), len(keyExists), "plainKeysToWitness and keysExist must have the same length")
 
 		ctx := context.Background()
 		ms := NewMockState(t)
@@ -2026,10 +2027,12 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 
 		toWitness := NewUpdates(ModeDirect, "", KeyToHexNibbleHash)
 		defer toWitness.Close()
-		if len(plainKeyToWitness) == length.Addr { // touch account
-			toWitness.TouchPlainKey(string(plainKeyToWitness), nil, toProcess.TouchAccount)
-		} else {
-			toWitness.TouchPlainKey(string(plainKeyToWitness), nil, toProcess.TouchStorage)
+		for _, plainKeyToWitness := range plainKeysToWitness {
+			if len(plainKeyToWitness) == length.Addr { // touch account
+				toWitness.TouchPlainKey(string(plainKeyToWitness), nil, toProcess.TouchAccount)
+			} else {
+				toWitness.TouchPlainKey(string(plainKeyToWitness), nil, toProcess.TouchStorage)
+			}
 		}
 
 		witnessTrie, rootWitness, err := hph.GenerateWitness(context.Background(), toWitness, nil, "")
@@ -2039,16 +2042,19 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 		require.NotNil(t, rootWitness, "root witness should not be nil")
 		require.Equal(t, root, rootWitness, "root witness should have the same root hash as trie")
 
-		if keyExists { // to be checked only if key should exist
-			hashedKeyWitnessed, err := CompactKey(KeyToHexNibbleHash(plainKeyToWitness))
-			require.NoError(t, err)
-			var gotValue bool
-			if len(plainKeyToWitness) == length.Addr {
-				_, gotValue = witnessTrie.GetAccount(hashedKeyWitnessed)
-			} else {
-				_, gotValue = witnessTrie.Get(hashedKeyWitnessed)
+		for i, plainKeyToWitness := range plainKeysToWitness {
+			keyExists := keyExists[i]
+			if keyExists { // to be checked only if key should exist
+				hashedKeyWitnessed, err := CompactKey(KeyToHexNibbleHash(plainKeyToWitness))
+				require.NoError(t, err)
+				var gotValue bool
+				if len(plainKeyToWitness) == length.Addr {
+					_, gotValue = witnessTrie.GetAccount(hashedKeyWitnessed)
+				} else {
+					_, gotValue = witnessTrie.Get(hashedKeyWitnessed)
+				}
+				require.True(t, gotValue, "value not found in witness trie for key %x", plainKeyToWitness)
 			}
-			require.True(t, gotValue, "value not found in witness trie")
 		}
 	}
 
@@ -2061,7 +2067,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Balance(common.Bytes2Hex(plainKeysList[i]), uint64(i))
 		}
 
-		buildTrieAndWitness(t, builder, addrWithSingleton, true)
+		buildTrieAndWitness(t, builder, [][]byte{addrWithSingleton}, []bool{true})
 	})
 	t.Run("RandomAccountsOnly", func(t *testing.T) {
 		plainKeysList, _ := generatePlainKeysWithSameHashPrefix(t, nil, length.Addr, 0, 5)
@@ -2072,7 +2078,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Balance(common.Bytes2Hex(plainKeysList[i]), uint64(i))
 		}
 
-		buildTrieAndWitness(t, builder, addrWithSingleton, true /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrWithSingleton}, []bool{true} /* keyExists */)
 	})
 	t.Run("RandomAccountsOnlyWithCPrefix", func(t *testing.T) {
 		plainKeysList, _ := generatePlainKeysWithSameHashPrefix(t, nil, length.Addr, 4, 5)
@@ -2083,7 +2089,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Balance(common.Bytes2Hex(plainKeysList[i]), uint64(i))
 		}
 
-		buildTrieAndWitness(t, builder, addrWithSingleton, true /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrWithSingleton}, []bool{true} /* keyExists */)
 	})
 
 	t.Run("RandomAccountsOnly-Many", func(t *testing.T) {
@@ -2095,7 +2101,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Balance(common.Bytes2Hex(plainKeysList[i]), uint64(i))
 		}
 
-		buildTrieAndWitness(t, builder, addrWithSingleton, true /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrWithSingleton}, []bool{true} /* keyExists */)
 	})
 	t.Run("StorageSingleton", func(t *testing.T) {
 		plainKeysList, _ := generatePlainKeysWithSameHashPrefix(t, nil, length.Addr, 0, 2)
@@ -2116,7 +2122,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 		// fmt.Printf("addrWithSingleton %x\n", addrWithSingleton)
 		// builder.Storage(common.Bytes2Hex(addrWithSingleton), "01044c45500c49b2a2a5dde8dfc7d1e71c894b7b9081866bfd33d5552deed470", "00044c45500c49b2a2a5dde8dfc7d1e71c894b7b9081866bfd33d5552deed470")
 
-		buildTrieAndWitness(t, builder, addrWithSingleton, true /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrWithSingleton}, []bool{true} /* keyExists */)
 	})
 
 	t.Run("StorageSubtrieWithCommonPrefix", func(t *testing.T) {
@@ -2142,7 +2148,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			fmt.Printf("storage %x -> %x\n", storageKeysList[sl], storageKeysList[sl])
 		}
 
-		buildTrieAndWitness(t, builder, addrWithSingleton, true /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrWithSingleton}, []bool{true} /* keyExists */)
 	})
 
 	t.Run("NonExistentAccountProofBranchNodesOnly", func(t *testing.T) {
@@ -2176,7 +2182,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Balance(common.Bytes2Hex(plainKeysList[i]), uint64(i))
 			fmt.Printf("addr %x\n", plainKeysList[i])
 		}
-		buildTrieAndWitness(t, builder, addrToProve, false /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrToProve}, []bool{false} /* keyExists */)
 	})
 
 	t.Run("NonExistentAccountProofShortNodeToAccount", func(t *testing.T) {
@@ -2214,7 +2220,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 		// add a storage slot to spice up the test case
 		builder.Storage(common.Bytes2Hex(plainKeys52789[0]), "00044c45500c49b2a2a5dde8dfc7d1e71c894b7b9081866bfd33d5552deed470", "00044c45500c49b2a2a5dde8dfc7d1e71c894b7b9081866bfd33d5552deed470")
 
-		buildTrieAndWitness(t, builder, addrToProve, false /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrToProve}, []bool{false} /* keyExists */)
 	})
 
 	t.Run("NonExistentAccountProofShortNodeToFullNode", func(t *testing.T) {
@@ -2257,7 +2263,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 		// add a storage slot to spice up the test case
 		builder.Storage(common.Bytes2Hex(plainKeys527a[0]), "00044c45500c49b2a2a5dde8dfc7d1e71c894b7b9081866bfd33d5552deed470", "00044c45500c49b2a2a5dde8dfc7d1e71c894b7b9081866bfd33d5552deed470")
 
-		buildTrieAndWitness(t, builder, addrToProve, false /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrToProve}, []bool{false} /* keyExists */)
 	})
 
 	t.Run("SingletonStorage", func(t *testing.T) {
@@ -2283,7 +2289,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Storage(common.Bytes2Hex(addrToProve), common.Bytes2Hex(storagePlainKeysList[sl]), common.Bytes2Hex(storagePlainKeysList[sl]))
 			fmt.Printf("storage %x -> %x\n", storagePlainKeysList[sl], storagePlainKeysList[sl])
 		}
-		buildTrieAndWitness(t, builder, fullStorageKeyToProve, true)
+		buildTrieAndWitness(t, builder, [][]byte{fullStorageKeyToProve}, []bool{true})
 	})
 
 	t.Run("StorageRootIsShortNode", func(t *testing.T) {
@@ -2310,7 +2316,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Storage(common.Bytes2Hex(addrToProve), common.Bytes2Hex(storagePlainKeysList[sl]), common.Bytes2Hex(storagePlainKeysList[sl]))
 			fmt.Printf("storage %x -> %x\n", storagePlainKeysList[sl], storagePlainKeysList[sl])
 		}
-		buildTrieAndWitness(t, builder, fullStorageKeyToProve, true /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{fullStorageKeyToProve}, []bool{true} /* keyExists */)
 	})
 
 	t.Run("StorageRootIsFullNode", func(t *testing.T) {
@@ -2340,7 +2346,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Storage(common.Bytes2Hex(addrToProve), common.Bytes2Hex(storagePlainKeysList[sl]), common.Bytes2Hex(storagePlainKeysList[sl]))
 			fmt.Printf("storage %x -> %x\n", storagePlainKeysList[sl], storagePlainKeysList[sl])
 		}
-		buildTrieAndWitness(t, builder, fullStorageKeyToProve, true /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{fullStorageKeyToProve}, []bool{true} /* keyExists */)
 	})
 
 	t.Run("NonExistentStorageProofBranchNodesOnly", func(t *testing.T) {
@@ -2384,7 +2390,7 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			builder.Storage(common.Bytes2Hex(addrToProve), common.Bytes2Hex(storagePlainKeysList[sl]), common.Bytes2Hex(storagePlainKeysList[sl]))
 			fmt.Printf("storage %x -> %x\n", storagePlainKeysList[sl], storagePlainKeysList[sl])
 		}
-		buildTrieAndWitness(t, builder, fullStorageKeyToProve, false)
+		buildTrieAndWitness(t, builder, [][]byte{fullStorageKeyToProve}, []bool{false})
 	})
 
 	t.Run("NonExistentStorageProofShortNodeToValue", func(t *testing.T) {
@@ -2429,7 +2435,41 @@ func Test_WitnessTrie_GenerateWitness(t *testing.T) {
 			fmt.Printf("storage %x -> %x\n", storageKeysList[sl], storageKeysList[sl])
 		}
 
-		buildTrieAndWitness(t, builder, addrToProve, false /* keyExists */)
+		buildTrieAndWitness(t, builder, [][]byte{addrToProve}, []bool{false} /* keyExists */)
 	})
 
+	t.Run("MultiKeyWitness_AccountWithSingletonStorage", func(t *testing.T) {
+		t.Logf("MultiKeyWitness_AccountWithSingletonStorage")
+		// Account with hashed prefix 0x5
+		plainKeys5, _ := generatePlainKeysWithSameHashPrefix(t, []byte{0x5}, length.Addr, 1, 1)
+
+		// Account with hashed prefix 0xa that will have a singleton storage slot
+		plainKeysA, _ := generatePlainKeysWithSameHashPrefix(t, []byte{0xa}, length.Addr, 1, 1)
+		addrWithStorage := common.Copy(plainKeysA[0])
+
+		// Generate a singleton storage slot for the 0xa prefixed account
+		storagePlainKeysList, _ := generatePlainKeysWithSameHashPrefix(t, []byte{0x3}, length.Hash, 1, 1)
+		storageSlot := common.Copy(storagePlainKeysList[0])
+
+		// Full storage key = address + storage slot
+		fullStorageKey := common.Copy(addrWithStorage)
+		fullStorageKey = append(fullStorageKey, storageSlot...)
+		require.Equal(t, len(fullStorageKey), length.Addr+length.Hash)
+
+		builder := NewUpdateBuilder()
+		// Add balance to account with prefix 0x5
+		builder.Balance(common.Bytes2Hex(plainKeys5[0]), 100)
+		fmt.Printf("addr (prefix 0x5) %x\n", plainKeys5[0])
+
+		// Add balance to account with prefix 0xa
+		builder.Balance(common.Bytes2Hex(addrWithStorage), 200)
+		fmt.Printf("addr (prefix 0xa) %x\n", addrWithStorage)
+
+		// Add singleton storage to 0xa account
+		builder.Storage(common.Bytes2Hex(addrWithStorage), common.Bytes2Hex(storageSlot), common.Bytes2Hex(storageSlot))
+		fmt.Printf("storage %x -> %x\n", storageSlot, storageSlot)
+
+		// Generate witness for both the address and its storage slot
+		buildTrieAndWitness(t, builder, [][]byte{plainKeys5[0], fullStorageKey}, []bool{true, true})
+	})
 }
```
