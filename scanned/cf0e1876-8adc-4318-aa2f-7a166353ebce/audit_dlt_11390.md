# [?] fix(shplonk,fflonk): validate proof shape in BatchVerify to prevent panics (#892)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark-crypto
Published: 2026-09-29
Source: https://github.com/Consensys-Incorporated/gnark-crypto/commit/c28a216a3e9f4793bfe1fd7a8f14ee3297e8f412
Type: security-commit

## Details
fix(shplonk,fflonk): validate proof shape in BatchVerify to prevent panics (#892)

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

## Patch
### ecc/bls12-377/fflonk/fflonk.go
```diff
@@ -150,8 +150,24 @@ func BatchVerify(proof OpeningProof, digests []kzg.Digest, points [][]fr.Element
 
 	// step 0: consistency checks between the folded claimed values of shplonk and the claimed
 	// values at the powers of the Sᵢ
+
+	// the outer dimensions must all agree, otherwise the loops below index past
+	// the end of one of the slices on a malformed proof
+	if len(digests) != len(points) ||
+		len(digests) != len(proof.ClaimedValues) ||
+		len(digests) != len(proof.SOpeningProof.ClaimedValues) {
+		return ErrNbPolynomialsNbPoints
+	}
+
 	for i := range len(proof.ClaimedValues) {
+		if len(proof.ClaimedValues[i]) == 0 {
+			return ErrNbPolynomialsNbPoints
+		}
 		sizeSi := len(proof.ClaimedValues[i][0])
+		// each pack is opened on the whole set Sᵢ
+		if sizeSi != len(points[i]) {
+			return ErrNbPolynomialsNbPoints
+		}
 		for j := 1; j < len(proof.ClaimedValues[i]); j++ {
 			// each set of opening must be of the same size (openings on powers of Si)
 			if sizeSi != len(proof.ClaimedValues[i][j]) {
```

### ecc/bls12-377/fflonk/fflonk_test.go
```diff
@@ -120,6 +120,131 @@ func TestFflonk(t *testing.T) {
 
 }
 
+// TestBatchVerifyMalformedShape checks that BatchVerify rejects proofs whose
+// dimensions are inconsistent instead of panicking with an index out of range.
+// All of these shapes are reachable from deserialised, attacker supplied data.
+func TestBatchVerifyMalformedShape(t *testing.T) {
+
+	assert := require.New(t)
+
+	// build one valid proof, then deform it in various ways
+	nbSets := 3
+	p := make([][][]fr.Element, nbSets)
+	for i := range nbSets {
+		nbPolysInSet := 4
+		p[i] = make([][]fr.Element, nbPolysInSet)
+		for j := range nbPolysInSet {
+			curSizePoly := j + 10
+			p[i][j] = make([]fr.Element, curSizePoly)
+			for k := range curSizePoly {
+				p[i][j][k].MustSetRandom()
+			}
+		}
+	}
+
+	x := make([][]fr.Element, nbSets)
+	for i := range nbSets {
+		curSetSize := i + 4
+		x[i] = make([]fr.Element, curSetSize)
+		for j := range curSetSize {
+			x[i][j].MustSetRandom()
+		}
+	}
+
+	digests := make([]kzg.Digest, nbSets)
+	var err error
+	for i := range nbSets {
+		digests[i], err = FoldAndCommit(p[i], testSrs.Pk)
+		assert.NoError(err)
+	}
+
+	hf := sha256.New()
+	validProof, err := BatchOpen(p, digests, x, hf, testSrs.Pk)
+	assert.NoError(err)
+	assert.NoError(BatchVerify(validProof, digests, x, hf, testSrs.Vk))
+
+	// deep copy so that each subtest starts from the valid proof
+	cloneProof := func() OpeningProof {
+		var c OpeningProof
+		c.SOpeningProof.W = validProof.SOpeningProof.W
+		c.SOpeningProof.WPrime = validProof.SOpeningProof.WPrime
+		c.SOpeningProof.ClaimedValues = make([][]fr.Element, len(validProof.SOpeningProof.ClaimedValues))
+		for i := range c.SOpeningProof.ClaimedValues {
+			c.SOpeningProof.ClaimedValues[i] = append([]fr.Element{}, validProof.SOpeningProof.ClaimedValues[i]...)
+		}
+		c.ClaimedValues = make([][][]fr.Element, len(validProof.ClaimedValues))
+		for i := range c.ClaimedValues {
+			c.ClaimedValues[i] = make([][]fr.Element, len(validProof.ClaimedValues[i]))
+			for j := range c.ClaimedValues[i] {
+				c.ClaimedValues[i][j] = append([]fr.Element{}, validProof.ClaimedValues[i][j]...)
+			}
+		}
+		return c
+	}
+	clonePoints := func() [][]fr.Element {
+		c := make([][]fr.Element, len(x))
+		for i := range x {
+			c[i] = append([]fr.Element{}, x[i]...)
+		}
+		return c
+	}
+
+	testCases := []struct {
+		name   string
+		deform func(proof *OpeningProof, digests *[]kzg.Digest, points *[][]fr.Element)
+	}{
+		{
+			name: "empty pack in ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues[0] = nil
+			},
+		},
+		{
+			name: "SOpeningProof.ClaimedValues shorter than ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.SOpeningProof.ClaimedValues = proof.SOpeningProof.ClaimedValues[:len(proof.SOpeningProof.ClaimedValues)-1]
+			},
+		},
+		{
+			name: "points row shorter than the claimed row",
+			deform: func(_ *OpeningProof, _ *[]kzg.Digest, points *[][]fr.Element) {
+				(*points)[0] = (*points)[0][:len((*points)[0])-1]
+			},
+		},
+		{
+			name: "points longer than ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues = proof.ClaimedValues[:len(proof.ClaimedValues)-1]
+			},
+		},
+		{
+			name: "digests shorter than points",
+			deform: func(_ *OpeningProof, digests *[]kzg.Digest, _ *[][]fr.Element) {
+				*digests = (*digests)[:len(*digests)-1]
+			},
+		},
+		{
+			name: "inconsistent row sizes within a pack",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues[0][1] = proof.ClaimedValues[0][1][:len(proof.ClaimedValues[0][1])-1]
+			},
+		},
+	}
+
+	for _, tc := range testCases {
+		t.Run(tc.name, func(t *testing.T) {
+			proof := cloneProof()
+			points := clonePoints()
+			ds := append([]kzg.Digest{}, digests...)
+			tc.deform(&proof, &ds, &points)
+
+			// must return an error, and in particular must not panic
+			err := BatchVerify(proof, ds, points, sha256.New(), testSrs.Vk)
+			require.Error(t, err)
+		})
+	}
+}
+
 func TestCommit(t *testing.T) {
 
 	assert := require.New(t)
```

### ecc/bls12-377/marshal.go
```diff
@@ -157,6 +157,9 @@ func (dec *Decoder) Decode(v any) (err error) {
 		for i := range *t {
 			read64, err = (*fr.Vector)(&(*t)[i]).ReadFrom(dec.r)
 			dec.n += read64
+			if err != nil {
+				return
+			}
 		}
 		return
 	case *[][][]fr.Element:
@@ -176,6 +179,9 @@ func (dec *Decoder) Decode(v any) (err error) {
 			for j := range (*t)[i] {
 				read64, err = (*fr.Vector)(&(*t)[i][j]).ReadFrom(dec.r)
 				dec.n += read64
+				if err != nil {
+					return
+				}
 			}
 		}
 		return
```

### ecc/bls12-377/marshal_test.go
```diff
@@ -166,6 +166,52 @@ func TestEncoder(t *testing.T) {
 	testDecode(t, &bufRaw, encRaw.BytesWritten())
 
 }
+
+// TestDecoderNestedError ensures that an error raised while decoding a nested
+// vector is not masked by a subsequent, well formed (possibly empty) one. The
+// decoding loops used to overwrite err on each iteration, so a trailing empty
+// row reported success on input that was in fact malformed.
+func TestDecoderNestedError(t *testing.T) {
+	t.Parallel()
+
+	// an element larger than the modulus: rejected by fr.Vector.ReadFrom
+	noncanonical := make([]byte, fr.Bytes)
+	for i := range noncanonical {
+		noncanonical[i] = 0xff
+	}
+
+	// uint32 big endian length prefix, as written by the encoder
+	length := func(n uint32) []byte {
+		return []byte{byte(n >> 24), byte(n >> 16), byte(n >> 8), byte(n)}
+	}
+
+	t.Run("slice²(elements)", func(t *testing.T) {
+		var buf bytes.Buffer
+		buf.Write(length(2))    // 2 rows
+		buf.Write(length(1))    // row 0: 1 element...
+		buf.Write(noncanonical) // ...which is noncanonical
+		buf.Write(length(0))    // row 1: empty, used to reset err to nil
+
+		var out [][]fr.Element
+		if err := NewDecoder(&buf).Decode(&out); err == nil {
+			t.Fatal("decoding a noncanonical element followed by an empty row must fail")
+		}
+	})
+
+	t.Run("slice³(elements)", func(t *testing.T) {
+		var buf bytes.Buffer
+		buf.Write(length(1))    // 1 pack
+		buf.Write(length(2))    // pack 0: 2 rows
+		buf.Write(length(1))    // row 0: 1 element...
+		buf.Write(noncanonical) // ...which is noncanonical
+		buf.Write(length(0))    // row 1: empty, used to reset err to nil
+
+		var out [][][]fr.Element
+		if err := NewDecoder(&buf).Decode(&out); err == nil {
+			t.Fatal("decoding a noncanonical element followed by an empty row must fail")
+		}
+	})
+}
 func TestIsCompressed(t *testing.T) {
 	t.Parallel()
 	var g1Inf, g1 G1Affine
```

### ecc/bls12-377/shplonk/shplonk.go
```diff
@@ -185,6 +185,11 @@ func BatchVerify(proof OpeningProof, digests []kzg.Digest, points [][]fr.Element
 	if len(digests) != len(points) {
 		return ErrInvalidNumberOfPoints
 	}
+	for i := range len(points) {
+		if len(proof.ClaimedValues[i]) != len(points[i]) {
+			return ErrInvalidNumberOfPoints
+		}
+	}
 
 	pointsToCheck := make([]bls12377.G1Affine, 0, len(digests)+2)
 	pointsToCheck = append(pointsToCheck, digests...)
```

### ecc/bls12-381/fflonk/fflonk.go
```diff
@@ -150,8 +150,24 @@ func BatchVerify(proof OpeningProof, digests []kzg.Digest, points [][]fr.Element
 
 	// step 0: consistency checks between the folded claimed values of shplonk and the claimed
 	// values at the powers of the Sᵢ
+
+	// the outer dimensions must all agree, otherwise the loops below index past
+	// the end of one of the slices on a malformed proof
+	if len(digests) != len(points) ||
+		len(digests) != len(proof.ClaimedValues) ||
+		len(digests) != len(proof.SOpeningProof.ClaimedValues) {
+		return ErrNbPolynomialsNbPoints
+	}
+
 	for i := range len(proof.ClaimedValues) {
+		if len(proof.ClaimedValues[i]) == 0 {
+			return ErrNbPolynomialsNbPoints
+		}
 		sizeSi := len(proof.ClaimedValues[i][0])
+		// each pack is opened on the whole set Sᵢ
+		if sizeSi != len(points[i]) {
+			return ErrNbPolynomialsNbPoints
+		}
 		for j := 1; j < len(proof.ClaimedValues[i]); j++ {
 			// each set of opening must be of the same size (openings on powers of Si)
 			if sizeSi != len(proof.ClaimedValues[i][j]) {
```

### ecc/bls12-381/fflonk/fflonk_test.go
```diff
@@ -120,6 +120,131 @@ func TestFflonk(t *testing.T) {
 
 }
 
+// TestBatchVerifyMalformedShape checks that BatchVerify rejects proofs whose
+// dimensions are inconsistent instead of panicking with an index out of range.
+// All of these shapes are reachable from deserialised, attacker supplied data.
+func TestBatchVerifyMalformedShape(t *testing.T) {
+
+	assert := require.New(t)
+
+	// build one valid proof, then deform it in various ways
+	nbSets := 3
+	p := make([][][]fr.Element, nbSets)
+	for i := range nbSets {
+		nbPolysInSet := 4
+		p[i] = make([][]fr.Element, nbPolysInSet)
+		for j := range nbPolysInSet {
+			curSizePoly := j + 10
+			p[i][j] = make([]fr.Element, curSizePoly)
+			for k := range curSizePoly {
+				p[i][j][k].MustSetRandom()
+			}
+		}
+	}
+
+	x := make([][]fr.Element, nbSets)
+	for i := range nbSets {
+		curSetSize := i + 4
+		x[i] = make([]fr.Element, curSetSize)
+		for j := range curSetSize {
+			x[i][j].MustSetRandom()
+		}
+	}
+
+	digests := make([]kzg.Digest, nbSets)
+	var err error
+	for i := range nbSets {
+		digests[i], err = FoldAndCommit(p[i], testSrs.Pk)
+		assert.NoError(err)
+	}
+
+	hf := sha256.New()
+	validProof, err := BatchOpen(p, digests, x, hf, testSrs.Pk)
+	assert.NoError(err)
+	assert.NoError(BatchVerify(validProof, digests, x, hf, testSrs.Vk))
+
+	// deep copy so that each subtest starts from the valid proof
+	cloneProof := func() OpeningProof {
+		var c OpeningProof
+		c.SOpeningProof.W = validProof.SOpeningProof.W
+		c.SOpeningProof.WPrime = validProof.SOpeningProof.WPrime
+		c.SOpeningProof.ClaimedValues = make([][]fr.Element, len(validProof.SOpeningProof.ClaimedValues))
+		for i := range c.SOpeningProof.ClaimedValues {
+			c.SOpeningProof.ClaimedValues[i] = append([]fr.Element{}, validProof.SOpeningProof.ClaimedValues[i]...)
+		}
+		c.ClaimedValues = make([][][]fr.Element, len(validProof.ClaimedValues))
+		for i := range c.ClaimedValues {
+			c.ClaimedValues[i] = make([][]fr.Element, len(validProof.ClaimedValues[i]))
+			for j := range c.ClaimedValues[i] {
+				c.ClaimedValues[i][j] = append([]fr.Element{}, validProof.ClaimedValues[i][j]...)
+			}
+		}
+		return c
+	}
+	clonePoints := func() [][]fr.Element {
+		c := make([][]fr.Element, len(x))
+		for i := range x {
+			c[i] = append([]fr.Element{}, x[i]...)
+		}
+		return c
+	}
+
+	testCases := []struct {
+		name   string
+		deform func(proof *OpeningProof, digests *[]kzg.Digest, points *[][]fr.Element)
+	}{
+		{
+			name: "empty pack in ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues[0] = nil
+			},
+		},
+		{
+			name: "SOpeningProof.ClaimedValues shorter than ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.SOpeningProof.ClaimedValues = proof.SOpeningProof.ClaimedValues[:len(proof.SOpeningProof.ClaimedValues)-1]
+			},
+		},
+		{
+			name: "points row shorter than the claimed row",
+			deform: func(_ *OpeningProof, _ *[]kzg.Digest, points *[][]fr.Element) {
+				(*points)[0] = (*points)[0][:len((*points)[0])-1]
+			},
+		},
+		{
+			name: "points longer than ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues = proof.ClaimedValues[:len(proof.ClaimedValues)-1]
+			},
+		},
+		{
+			name: "digests shorter than points",
+			deform: func(_ *OpeningProof, digests *[]kzg.Digest, _ *[][]fr.Element) {
+				*digests = (*digests)[:len(*digests)-1]
+			},
+		},
+		{
+			name: "inconsistent row sizes within a pack",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues[0][1] = proof.ClaimedValues[0][1][:len(proof.ClaimedValues[0][1])-1]
+			},
+		},
+	}
+
+	for _, tc := range testCases {
+		t.Run(tc.name, func(t *testing.T) {
+			proof := cloneProof()
+			points := clonePoints()
+			ds := append([]kzg.Digest{}, digests...)
+			tc.deform(&proof, &ds, &points)
+
+			// must return an error, and in particular must not panic
+			err := BatchVerify(proof, ds, points, sha256.New(), testSrs.Vk)
+			require.Error(t, err)
+		})
+	}
+}
+
 func TestCommit(t *testing.T) {
 
 	assert := require.New(t)
```

### ecc/bls12-381/marshal.go
```diff
@@ -157,6 +157,9 @@ func (dec *Decoder) Decode(v any) (err error) {
 		for i := range *t {
 			read64, err = (*fr.Vector)(&(*t)[i]).ReadFrom(dec.r)
 			dec.n += read64
+			if err != nil {
+				return
+			}
 		}
 		return
 	case *[][][]fr.Element:
@@ -176,6 +179,9 @@ func (dec *Decoder) Decode(v any) (err error) {
 			for j := range (*t)[i] {
 				read64, err = (*fr.Vector)(&(*t)[i][j]).ReadFrom(dec.r)
 				dec.n += read64
+				if err != nil {
+					return
+				}
 			}
 		}
 		return
```

### ecc/bls12-381/marshal_test.go
```diff
@@ -166,6 +166,52 @@ func TestEncoder(t *testing.T) {
 	testDecode(t, &bufRaw, encRaw.BytesWritten())
 
 }
+
+// TestDecoderNestedError ensures that an error raised while decoding a nested
+// vector is not masked by a subsequent, well formed (possibly empty) one. The
+// decoding loops used to overwrite err on each iteration, so a trailing empty
+// row reported success on input that was in fact malformed.
+func TestDecoderNestedError(t *testing.T) {
+	t.Parallel()
+
+	// an element larger than the modulus: rejected by fr.Vector.ReadFrom
+	noncanonical := make([]byte, fr.Bytes)
+	for i := range noncanonical {
+		noncanonical[i] = 0xff
+	}
+
+	// uint32 big endian length prefix, as written by the encoder
+	length := func(n uint32) []byte {
+		return []byte{byte(n >> 24), byte(n >> 16), byte(n >> 8), byte(n)}
+	}
+
+	t.Run("slice²(elements)", func(t *testing.T) {
+		var buf bytes.Buffer
+		buf.Write(length(2))    // 2 rows
+		buf.Write(length(1))    // row 0: 1 element...
+		buf.Write(noncanonical) // ...which is noncanonical
+		buf.Write(length(0))    // row 1: empty, used to reset err to nil
+
+		var out [][]fr.Element
+		if err := NewDecoder(&buf).Decode(&out); err == nil {
+			t.Fatal("decoding a noncanonical element followed by an empty row must fail")
+		}
+	})
+
+	t.Run("slice³(elements)", func(t *testing.T) {
+		var buf bytes.Buffer
+		buf.Write(length(1))    // 1 pack
+		buf.Write(length(2))    // pack 0: 2 rows
+		buf.Write(length(1))    // row 0: 1 element...
+		buf.Write(noncanonical) // ...which is noncanonical
+		buf.Write(length(0))    // row 1: empty, used to reset err to nil
+
+		var out [][][]fr.Element
+		if err := NewDecoder(&buf).Decode(&out); err == nil {
+			t.Fatal("decoding a noncanonical element followed by an empty row must fail")
+		}
+	})
+}
 func TestIsCompressed(t *testing.T) {
 	t.Parallel()
 	var g1Inf, g1 G1Affine
```

### ecc/bls12-381/shplonk/shplonk.go
```diff
@@ -185,6 +185,11 @@ func BatchVerify(proof OpeningProof, digests []kzg.Digest, points [][]fr.Element
 	if len(digests) != len(points) {
 		return ErrInvalidNumberOfPoints
 	}
+	for i := range len(points) {
+		if len(proof.ClaimedValues[i]) != len(points[i]) {
+			return ErrInvalidNumberOfPoints
+		}
+	}
 
 	pointsToCheck := make([]bls12381.G1Affine, 0, len(digests)+2)
 	pointsToCheck = append(pointsToCheck, digests...)
```

### ecc/bls24-315/fflonk/fflonk.go
```diff
@@ -150,8 +150,24 @@ func BatchVerify(proof OpeningProof, digests []kzg.Digest, points [][]fr.Element
 
 	// step 0: consistency checks between the folded claimed values of shplonk and the claimed
 	// values at the powers of the Sᵢ
+
+	// the outer dimensions must all agree, otherwise the loops below index past
+	// the end of one of the slices on a malformed proof
+	if len(digests) != len(points) ||
+		len(digests) != len(proof.ClaimedValues) ||
+		len(digests) != len(proof.SOpeningProof.ClaimedValues) {
+		return ErrNbPolynomialsNbPoints
+	}
+
 	for i := range len(proof.ClaimedValues) {
+		if len(proof.ClaimedValues[i]) == 0 {
+			return ErrNbPolynomialsNbPoints
+		}
 		sizeSi := len(proof.ClaimedValues[i][0])
+		// each pack is opened on the whole set Sᵢ
+		if sizeSi != len(points[i]) {
+			return ErrNbPolynomialsNbPoints
+		}
 		for j := 1; j < len(proof.ClaimedValues[i]); j++ {
 			// each set of opening must be of the same size (openings on powers of Si)
 			if sizeSi != len(proof.ClaimedValues[i][j]) {
```

### ecc/bls24-315/fflonk/fflonk_test.go
```diff
@@ -120,6 +120,131 @@ func TestFflonk(t *testing.T) {
 
 }
 
+// TestBatchVerifyMalformedShape checks that BatchVerify rejects proofs whose
+// dimensions are inconsistent instead of panicking with an index out of range.
+// All of these shapes are reachable from deserialised, attacker supplied data.
+func TestBatchVerifyMalformedShape(t *testing.T) {
+
+	assert := require.New(t)
+
+	// build one valid proof, then deform it in various ways
+	nbSets := 3
+	p := make([][][]fr.Element, nbSets)
+	for i := range nbSets {
+		nbPolysInSet := 4
+		p[i] = make([][]fr.Element, nbPolysInSet)
+		for j := range nbPolysInSet {
+			curSizePoly := j + 10
+			p[i][j] = make([]fr.Element, curSizePoly)
+			for k := range curSizePoly {
+				p[i][j][k].MustSetRandom()
+			}
+		}
+	}
+
+	x := make([][]fr.Element, nbSets)
+	for i := range nbSets {
+		curSetSize := i + 4
+		x[i] = make([]fr.Element, curSetSize)
+		for j := range curSetSize {
+			x[i][j].MustSetRandom()
+		}
+	}
+
+	digests := make([]kzg.Digest, nbSets)
+	var err error
+	for i := range nbSets {
+		digests[i], err = FoldAndCommit(p[i], testSrs.Pk)
+		assert.NoError(err)
+	}
+
+	hf := sha256.New()
+	validProof, err := BatchOpen(p, digests, x, hf, testSrs.Pk)
+	assert.NoError(err)
+	assert.NoError(BatchVerify(validProof, digests, x, hf, testSrs.Vk))
+
+	// deep copy so that each subtest starts from the valid proof
+	cloneProof := func() OpeningProof {
+		var c OpeningProof
+		c.SOpeningProof.W = validProof.SOpeningProof.W
+		c.SOpeningProof.WPrime = validProof.SOpeningProof.WPrime
+		c.SOpeningProof.ClaimedValues = make([][]fr.Element, len(validProof.SOpeningProof.ClaimedValues))
+		for i := range c.SOpeningProof.ClaimedValues {
+			c.SOpeningProof.ClaimedValues[i] = append([]fr.Element{}, validProof.SOpeningProof.ClaimedValues[i]...)
+		}
+		c.ClaimedValues = make([][][]fr.Element, len(validProof.ClaimedValues))
+		for i := range c.ClaimedValues {
+			c.ClaimedValues[i] = make([][]fr.Element, len(validProof.ClaimedValues[i]))
+			for j := range c.ClaimedValues[i] {
+				c.ClaimedValues[i][j] = append([]fr.Element{}, validProof.ClaimedValues[i][j]...)
+			}
+		}
+		return c
+	}
+	clonePoints := func() [][]fr.Element {
+		c := make([][]fr.Element, len(x))
+		for i := range x {
+			c[i] = append([]fr.Element{}, x[i]...)
+		}
+		return c
+	}
+
+	testCases := []struct {
+		name   string
+		deform func(proof *OpeningProof, digests *[]kzg.Digest, points *[][]fr.Element)
+	}{
+		{
+			name: "empty pack in ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues[0] = nil
+			},
+		},
+		{
+			name: "SOpeningProof.ClaimedValues shorter than ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.SOpeningProof.ClaimedValues = proof.SOpeningProof.ClaimedValues[:len(proof.SOpeningProof.ClaimedValues)-1]
+			},
+		},
+		{
+			name: "points row shorter than the claimed row",
+			deform: func(_ *OpeningProof, _ *[]kzg.Digest, points *[][]fr.Element) {
+				(*points)[0] = (*points)[0][:len((*points)[0])-1]
+			},
+		},
+		{
+			name: "points longer than ClaimedValues",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues = proof.ClaimedValues[:len(proof.ClaimedValues)-1]
+			},
+		},
+		{
+			name: "digests shorter than points",
+			deform: func(_ *OpeningProof, digests *[]kzg.Digest, _ *[][]fr.Element) {
+				*digests = (*digests)[:len(*digests)-1]
+			},
+		},
+		{
+			name: "inconsistent row sizes within a pack",
+			deform: func(proof *OpeningProof, _ *[]kzg.Digest, _ *[][]fr.Element) {
+				proof.ClaimedValues[0][1] = proof.ClaimedValues[0][1][:len(proof.ClaimedValues[0][1])-1]
+			},
+		},
+	}
+
+	for _, tc := range testCases {
+		t.Run(tc.name, func(t *testing.T) {
+			proof := cloneProof()
+			points := clonePoints()
+			ds := append([]kzg.Digest{}, digests...)
+			tc.deform(&proof, &ds, &points)
+
+			// must return an error, and in particular must not panic
+			err := BatchVerify(proof, ds, points, sha256.New(), testSrs.Vk)
+			require.Error(t, err)
+		})
+	}
+}
+
 func TestCommit(t *testing.T) {
 
 	assert := require.New(t)
```
