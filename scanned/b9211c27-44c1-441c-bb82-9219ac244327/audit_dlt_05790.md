# [?] fix(bits): prevent BitArray.UnmarshalJSON from crashing on 0 bits in the JSON (#2774)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-04-11
Source: https://github.com/cometbft/cometbft/commit/75d12c32b8f8c504490096082b6217b87f5112ed
Type: security-commit

## Details
fix(bits): prevent BitArray.UnmarshalJSON from crashing on 0 bits in the JSON (#2774)

This change fixes a bug in which BitArray.UnmarshalJSON hadn't accounted
for the fact that invoking NewBitArray(<=0) returns nil and hence when
dereferenced would crash with a runtime nil pointer dereference. This
bug was found by my security analysis and fuzzing too.

Author: @odeke-em 

Fixes https://github.com/cometbft/cometbft/issues/2658

---

#### PR checklist

- [x] Tests written/updated
- [x] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] ~~Updated relevant documentation (`docs/` or `spec/`) and code
comments~~
- [x] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

---------

Co-authored-by: Emmanuel T Odeke <emmanuel@orijtech.com>

## Patch
### .changelog/unreleased/bug-fixes/2774-bitarray-unmarshal-json.md
```diff
@@ -0,0 +1,2 @@
+- [`bits`] prevent `BitArray.UnmarshalJSON` from crashing on 0 bits
+  ([\#2774](https://github.com/cometbft/cometbft/pull/2774))
```

### internal/bits/bit_array.go
```diff
@@ -409,6 +409,13 @@ func (bA *BitArray) UnmarshalJSON(bz []byte) error {
 	// Construct new BitArray and copy over.
 	numBits := len(bits)
 	bA2 := NewBitArray(numBits)
+	if bA2 == nil {
+		// Treat it as if we encountered the case: b == "null"
+		bA.Bits = 0
+		bA.Elems = nil
+		return nil
+	}
+
 	for i := 0; i < numBits; i++ {
 		if bits[i] == 'x' {
 			bA2.SetIndex(i, true)
```

### internal/bits/bit_array_test.go
```diff
@@ -286,3 +286,18 @@ func TestBitArrayProtoBuf(t *testing.T) {
 		}
 	}
 }
+
+// Tests that UnmarshalJSON doesn't crash when no bits are passed into the JSON.
+// See issue https://github.com/cometbft/cometbft/issues/2658
+func TestUnmarshalJSONDoesntCrashOnZeroBits(t *testing.T) {
+	type indexCorpus struct {
+		BitArray *BitArray `json:"ba"`
+		Index    int       `json:"i"`
+	}
+
+	ic := new(indexCorpus)
+	blob := []byte(`{"BA":""}`)
+	err := json.Unmarshal(blob, ic)
+	require.NoError(t, err)
+	require.Equal(t, ic.BitArray, &BitArray{Bits: 0, Elems: nil})
+}
```
