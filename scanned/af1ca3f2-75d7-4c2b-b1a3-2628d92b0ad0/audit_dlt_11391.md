# [?] fix(fft): validate domain cardinality in `ReadFrom` to prevent panic/OOM (#893)

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark-crypto
Published: 2026-09-29
Source: https://github.com/Consensys-Incorporated/gnark-crypto/commit/5e563f61a52928b28227a7f83a9024746764ebb2
Type: security-commit

## Details
fix(fft): validate domain cardinality in `ReadFrom` to prevent panic/OOM (#893)

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

## Patch
### ecc/bls12-377/fr/fft/domain.go
```diff
@@ -377,7 +377,15 @@ func (d *Domain) WriteTo(w io.Writer) (int64, error) {
 	return written, nil
 }
 
-// ReadFrom attempts to decode a domain from Reader
+// ReadFrom attempts to decode a domain from Reader.
+//
+// It rejects a cardinality that is not a power of two or that exceeds the
+// field's 2-adicity, and checks the decoded elements for consistency with the
+// cardinality and with one another.
+//
+// It does not impose a resource limit: a cardinality may be valid and still
+// large, and the precomputation it triggers allocates memory linear in the
+// cardinality. Callers decoding untrusted input must bound the size themselves.
 func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 
 	var read int64
@@ -389,21 +397,52 @@ func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 	}
 	read += 8
 
+	// Cardinality must be a non-zero power of 2 within the field's 2-adicity.
+	if d.Cardinality == 0 || bits.OnesCount64(d.Cardinality) != 1 {
+		return read, errors.New("fft: invalid domain cardinality: must be a non-zero power of 2")
+	}
+	// Generator is deterministic in the cardinality, so it doubles as the
+	// 2-adicity bound check and as the expected value for d.Generator below.
+	generator, err := Generator(d.Cardinality)
+	if err != nil {
+		return read, err
+	}
+
 	toDecode := []*fr.Element{&d.CardinalityInv, &d.Generator, &d.GeneratorInv, &d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv}
 
 	for _, v := range toDecode {
 		var buf [fr.Bytes]byte
-		_, err = r.Read(buf[:])
+		// io.Reader may return fewer than len(buf) bytes without an error, so
+		// read the element in full rather than decoding a truncated buffer.
+		n, err := io.ReadFull(r, buf[:])
+		read += int64(n)
 		if err != nil {
 			return read, err
 		}
-		read += fr.Bytes
 		*v, err = fr.BigEndian.Element(&buf)
 		if err != nil {
 			return read, err
 		}
 	}
 
+	// The decoded elements are individually valid field elements; check that
+	// they also describe this domain.
+	if !d.Generator.Equal(&generator) {
+		return read, errors.New("fft: invalid domain: generator does not match cardinality")
+	}
+	var check fr.Element
+	if !check.Mul(&d.Generator, &d.GeneratorInv).IsOne() {
+		return read, errors.New("fft: invalid domain: generator inverse mismatch")
+	}
+	if !check.SetUint64(d.Cardinality).Mul(&check, &d.CardinalityInv).IsOne() {
+		return read, errors.New("fft: invalid domain: cardinality inverse mismatch")
+	}
+	// FrMultiplicativeGen is caller-chosen (see WithShift), so only its inverse
+	// can be checked.
+	if !check.Mul(&d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv).IsOne() {
+		return read, errors.New("fft: invalid domain: multiplicative generator inverse mismatch")
+	}
+
 	err = binary.Read(r, binary.BigEndian, &d.withPrecompute)
 	if err != nil {
 		return read, err
```

### ecc/bls12-377/fr/fft/domain_test.go
```diff
@@ -39,6 +39,66 @@ func TestDomainSerialization(t *testing.T) {
 	}
 }
 
+func TestDomainDeserializationInvalid(t *testing.T) {
+	assert := require.New(t)
+
+	valid := NewDomain(1 << 6)
+
+	// serialize returns the encoding of d, with the fields of a valid domain
+	// overwritten by tamper.
+	serialize := func(tamper func(d *Domain)) []byte {
+		d := *valid
+		tamper(&d)
+		var buf bytes.Buffer
+		_, err := d.WriteTo(&buf)
+		assert.NoError(err)
+		return buf.Bytes()
+	}
+
+	one := fr.One()
+
+	for _, tc := range []struct {
+		name string
+		data []byte
+	}{
+		{
+			// bits.TrailingZeros64(0) is 64, which used to size the twiddle
+			// allocations at 1<<63 and take the process down.
+			name: "zero cardinality",
+			data: serialize(func(d *Domain) { d.Cardinality = 0 }),
+		}, {
+			name: "cardinality not a power of 2",
+			data: serialize(func(d *Domain) { d.Cardinality = (1 << 6) + 1 }),
+		}, {
+			// beyond the 2-adicity of every supported field
+			name: "cardinality beyond 2-adicity",
+			data: serialize(func(d *Domain) { d.Cardinality = 1 << 63 }),
+		}, {
+			name: "generator does not match cardinality",
+			data: serialize(func(d *Domain) { d.Generator = one }),
+		}, {
+			name: "generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.GeneratorInv = one }),
+		}, {
+			name: "cardinality inverse mismatch",
+			data: serialize(func(d *Domain) { d.CardinalityInv = one }),
+		}, {
+			name: "multiplicative generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.FrMultiplicativeGenInv = one }),
+		}, {
+			// a short read must not decode a zero-padded element
+			name: "truncated element",
+			data: serialize(func(d *Domain) {})[:8+fr.Bytes+fr.Bytes/2],
+		},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			var d Domain
+			_, err := d.ReadFrom(bytes.NewReader(tc.data))
+			assert.Error(err, "invalid domain should be rejected")
+		})
+	}
+}
+
 func TestNewDomainCache(t *testing.T) {
 	t.Run("CacheWithoutShift", func(t *testing.T) {
 		key1 := domainCacheKey{
```

### ecc/bls12-381/fr/fft/domain.go
```diff
@@ -377,7 +377,15 @@ func (d *Domain) WriteTo(w io.Writer) (int64, error) {
 	return written, nil
 }
 
-// ReadFrom attempts to decode a domain from Reader
+// ReadFrom attempts to decode a domain from Reader.
+//
+// It rejects a cardinality that is not a power of two or that exceeds the
+// field's 2-adicity, and checks the decoded elements for consistency with the
+// cardinality and with one another.
+//
+// It does not impose a resource limit: a cardinality may be valid and still
+// large, and the precomputation it triggers allocates memory linear in the
+// cardinality. Callers decoding untrusted input must bound the size themselves.
 func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 
 	var read int64
@@ -389,21 +397,52 @@ func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 	}
 	read += 8
 
+	// Cardinality must be a non-zero power of 2 within the field's 2-adicity.
+	if d.Cardinality == 0 || bits.OnesCount64(d.Cardinality) != 1 {
+		return read, errors.New("fft: invalid domain cardinality: must be a non-zero power of 2")
+	}
+	// Generator is deterministic in the cardinality, so it doubles as the
+	// 2-adicity bound check and as the expected value for d.Generator below.
+	generator, err := Generator(d.Cardinality)
+	if err != nil {
+		return read, err
+	}
+
 	toDecode := []*fr.Element{&d.CardinalityInv, &d.Generator, &d.GeneratorInv, &d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv}
 
 	for _, v := range toDecode {
 		var buf [fr.Bytes]byte
-		_, err = r.Read(buf[:])
+		// io.Reader may return fewer than len(buf) bytes without an error, so
+		// read the element in full rather than decoding a truncated buffer.
+		n, err := io.ReadFull(r, buf[:])
+		read += int64(n)
 		if err != nil {
 			return read, err
 		}
-		read += fr.Bytes
 		*v, err = fr.BigEndian.Element(&buf)
 		if err != nil {
 			return read, err
 		}
 	}
 
+	// The decoded elements are individually valid field elements; check that
+	// they also describe this domain.
+	if !d.Generator.Equal(&generator) {
+		return read, errors.New("fft: invalid domain: generator does not match cardinality")
+	}
+	var check fr.Element
+	if !check.Mul(&d.Generator, &d.GeneratorInv).IsOne() {
+		return read, errors.New("fft: invalid domain: generator inverse mismatch")
+	}
+	if !check.SetUint64(d.Cardinality).Mul(&check, &d.CardinalityInv).IsOne() {
+		return read, errors.New("fft: invalid domain: cardinality inverse mismatch")
+	}
+	// FrMultiplicativeGen is caller-chosen (see WithShift), so only its inverse
+	// can be checked.
+	if !check.Mul(&d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv).IsOne() {
+		return read, errors.New("fft: invalid domain: multiplicative generator inverse mismatch")
+	}
+
 	err = binary.Read(r, binary.BigEndian, &d.withPrecompute)
 	if err != nil {
 		return read, err
```

### ecc/bls12-381/fr/fft/domain_test.go
```diff
@@ -39,6 +39,66 @@ func TestDomainSerialization(t *testing.T) {
 	}
 }
 
+func TestDomainDeserializationInvalid(t *testing.T) {
+	assert := require.New(t)
+
+	valid := NewDomain(1 << 6)
+
+	// serialize returns the encoding of d, with the fields of a valid domain
+	// overwritten by tamper.
+	serialize := func(tamper func(d *Domain)) []byte {
+		d := *valid
+		tamper(&d)
+		var buf bytes.Buffer
+		_, err := d.WriteTo(&buf)
+		assert.NoError(err)
+		return buf.Bytes()
+	}
+
+	one := fr.One()
+
+	for _, tc := range []struct {
+		name string
+		data []byte
+	}{
+		{
+			// bits.TrailingZeros64(0) is 64, which used to size the twiddle
+			// allocations at 1<<63 and take the process down.
+			name: "zero cardinality",
+			data: serialize(func(d *Domain) { d.Cardinality = 0 }),
+		}, {
+			name: "cardinality not a power of 2",
+			data: serialize(func(d *Domain) { d.Cardinality = (1 << 6) + 1 }),
+		}, {
+			// beyond the 2-adicity of every supported field
+			name: "cardinality beyond 2-adicity",
+			data: serialize(func(d *Domain) { d.Cardinality = 1 << 63 }),
+		}, {
+			name: "generator does not match cardinality",
+			data: serialize(func(d *Domain) { d.Generator = one }),
+		}, {
+			name: "generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.GeneratorInv = one }),
+		}, {
+			name: "cardinality inverse mismatch",
+			data: serialize(func(d *Domain) { d.CardinalityInv = one }),
+		}, {
+			name: "multiplicative generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.FrMultiplicativeGenInv = one }),
+		}, {
+			// a short read must not decode a zero-padded element
+			name: "truncated element",
+			data: serialize(func(d *Domain) {})[:8+fr.Bytes+fr.Bytes/2],
+		},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			var d Domain
+			_, err := d.ReadFrom(bytes.NewReader(tc.data))
+			assert.Error(err, "invalid domain should be rejected")
+		})
+	}
+}
+
 func TestNewDomainCache(t *testing.T) {
 	t.Run("CacheWithoutShift", func(t *testing.T) {
 		key1 := domainCacheKey{
```

### ecc/bls24-315/fr/fft/domain.go
```diff
@@ -377,7 +377,15 @@ func (d *Domain) WriteTo(w io.Writer) (int64, error) {
 	return written, nil
 }
 
-// ReadFrom attempts to decode a domain from Reader
+// ReadFrom attempts to decode a domain from Reader.
+//
+// It rejects a cardinality that is not a power of two or that exceeds the
+// field's 2-adicity, and checks the decoded elements for consistency with the
+// cardinality and with one another.
+//
+// It does not impose a resource limit: a cardinality may be valid and still
+// large, and the precomputation it triggers allocates memory linear in the
+// cardinality. Callers decoding untrusted input must bound the size themselves.
 func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 
 	var read int64
@@ -389,21 +397,52 @@ func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 	}
 	read += 8
 
+	// Cardinality must be a non-zero power of 2 within the field's 2-adicity.
+	if d.Cardinality == 0 || bits.OnesCount64(d.Cardinality) != 1 {
+		return read, errors.New("fft: invalid domain cardinality: must be a non-zero power of 2")
+	}
+	// Generator is deterministic in the cardinality, so it doubles as the
+	// 2-adicity bound check and as the expected value for d.Generator below.
+	generator, err := Generator(d.Cardinality)
+	if err != nil {
+		return read, err
+	}
+
 	toDecode := []*fr.Element{&d.CardinalityInv, &d.Generator, &d.GeneratorInv, &d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv}
 
 	for _, v := range toDecode {
 		var buf [fr.Bytes]byte
-		_, err = r.Read(buf[:])
+		// io.Reader may return fewer than len(buf) bytes without an error, so
+		// read the element in full rather than decoding a truncated buffer.
+		n, err := io.ReadFull(r, buf[:])
+		read += int64(n)
 		if err != nil {
 			return read, err
 		}
-		read += fr.Bytes
 		*v, err = fr.BigEndian.Element(&buf)
 		if err != nil {
 			return read, err
 		}
 	}
 
+	// The decoded elements are individually valid field elements; check that
+	// they also describe this domain.
+	if !d.Generator.Equal(&generator) {
+		return read, errors.New("fft: invalid domain: generator does not match cardinality")
+	}
+	var check fr.Element
+	if !check.Mul(&d.Generator, &d.GeneratorInv).IsOne() {
+		return read, errors.New("fft: invalid domain: generator inverse mismatch")
+	}
+	if !check.SetUint64(d.Cardinality).Mul(&check, &d.CardinalityInv).IsOne() {
+		return read, errors.New("fft: invalid domain: cardinality inverse mismatch")
+	}
+	// FrMultiplicativeGen is caller-chosen (see WithShift), so only its inverse
+	// can be checked.
+	if !check.Mul(&d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv).IsOne() {
+		return read, errors.New("fft: invalid domain: multiplicative generator inverse mismatch")
+	}
+
 	err = binary.Read(r, binary.BigEndian, &d.withPrecompute)
 	if err != nil {
 		return read, err
```

### ecc/bls24-315/fr/fft/domain_test.go
```diff
@@ -39,6 +39,66 @@ func TestDomainSerialization(t *testing.T) {
 	}
 }
 
+func TestDomainDeserializationInvalid(t *testing.T) {
+	assert := require.New(t)
+
+	valid := NewDomain(1 << 6)
+
+	// serialize returns the encoding of d, with the fields of a valid domain
+	// overwritten by tamper.
+	serialize := func(tamper func(d *Domain)) []byte {
+		d := *valid
+		tamper(&d)
+		var buf bytes.Buffer
+		_, err := d.WriteTo(&buf)
+		assert.NoError(err)
+		return buf.Bytes()
+	}
+
+	one := fr.One()
+
+	for _, tc := range []struct {
+		name string
+		data []byte
+	}{
+		{
+			// bits.TrailingZeros64(0) is 64, which used to size the twiddle
+			// allocations at 1<<63 and take the process down.
+			name: "zero cardinality",
+			data: serialize(func(d *Domain) { d.Cardinality = 0 }),
+		}, {
+			name: "cardinality not a power of 2",
+			data: serialize(func(d *Domain) { d.Cardinality = (1 << 6) + 1 }),
+		}, {
+			// beyond the 2-adicity of every supported field
+			name: "cardinality beyond 2-adicity",
+			data: serialize(func(d *Domain) { d.Cardinality = 1 << 63 }),
+		}, {
+			name: "generator does not match cardinality",
+			data: serialize(func(d *Domain) { d.Generator = one }),
+		}, {
+			name: "generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.GeneratorInv = one }),
+		}, {
+			name: "cardinality inverse mismatch",
+			data: serialize(func(d *Domain) { d.CardinalityInv = one }),
+		}, {
+			name: "multiplicative generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.FrMultiplicativeGenInv = one }),
+		}, {
+			// a short read must not decode a zero-padded element
+			name: "truncated element",
+			data: serialize(func(d *Domain) {})[:8+fr.Bytes+fr.Bytes/2],
+		},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			var d Domain
+			_, err := d.ReadFrom(bytes.NewReader(tc.data))
+			assert.Error(err, "invalid domain should be rejected")
+		})
+	}
+}
+
 func TestNewDomainCache(t *testing.T) {
 	t.Run("CacheWithoutShift", func(t *testing.T) {
 		key1 := domainCacheKey{
```

### ecc/bls24-317/fr/fft/domain.go
```diff
@@ -377,7 +377,15 @@ func (d *Domain) WriteTo(w io.Writer) (int64, error) {
 	return written, nil
 }
 
-// ReadFrom attempts to decode a domain from Reader
+// ReadFrom attempts to decode a domain from Reader.
+//
+// It rejects a cardinality that is not a power of two or that exceeds the
+// field's 2-adicity, and checks the decoded elements for consistency with the
+// cardinality and with one another.
+//
+// It does not impose a resource limit: a cardinality may be valid and still
+// large, and the precomputation it triggers allocates memory linear in the
+// cardinality. Callers decoding untrusted input must bound the size themselves.
 func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 
 	var read int64
@@ -389,21 +397,52 @@ func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 	}
 	read += 8
 
+	// Cardinality must be a non-zero power of 2 within the field's 2-adicity.
+	if d.Cardinality == 0 || bits.OnesCount64(d.Cardinality) != 1 {
+		return read, errors.New("fft: invalid domain cardinality: must be a non-zero power of 2")
+	}
+	// Generator is deterministic in the cardinality, so it doubles as the
+	// 2-adicity bound check and as the expected value for d.Generator below.
+	generator, err := Generator(d.Cardinality)
+	if err != nil {
+		return read, err
+	}
+
 	toDecode := []*fr.Element{&d.CardinalityInv, &d.Generator, &d.GeneratorInv, &d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv}
 
 	for _, v := range toDecode {
 		var buf [fr.Bytes]byte
-		_, err = r.Read(buf[:])
+		// io.Reader may return fewer than len(buf) bytes without an error, so
+		// read the element in full rather than decoding a truncated buffer.
+		n, err := io.ReadFull(r, buf[:])
+		read += int64(n)
 		if err != nil {
 			return read, err
 		}
-		read += fr.Bytes
 		*v, err = fr.BigEndian.Element(&buf)
 		if err != nil {
 			return read, err
 		}
 	}
 
+	// The decoded elements are individually valid field elements; check that
+	// they also describe this domain.
+	if !d.Generator.Equal(&generator) {
+		return read, errors.New("fft: invalid domain: generator does not match cardinality")
+	}
+	var check fr.Element
+	if !check.Mul(&d.Generator, &d.GeneratorInv).IsOne() {
+		return read, errors.New("fft: invalid domain: generator inverse mismatch")
+	}
+	if !check.SetUint64(d.Cardinality).Mul(&check, &d.CardinalityInv).IsOne() {
+		return read, errors.New("fft: invalid domain: cardinality inverse mismatch")
+	}
+	// FrMultiplicativeGen is caller-chosen (see WithShift), so only its inverse
+	// can be checked.
+	if !check.Mul(&d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv).IsOne() {
+		return read, errors.New("fft: invalid domain: multiplicative generator inverse mismatch")
+	}
+
 	err = binary.Read(r, binary.BigEndian, &d.withPrecompute)
 	if err != nil {
 		return read, err
```

### ecc/bls24-317/fr/fft/domain_test.go
```diff
@@ -39,6 +39,66 @@ func TestDomainSerialization(t *testing.T) {
 	}
 }
 
+func TestDomainDeserializationInvalid(t *testing.T) {
+	assert := require.New(t)
+
+	valid := NewDomain(1 << 6)
+
+	// serialize returns the encoding of d, with the fields of a valid domain
+	// overwritten by tamper.
+	serialize := func(tamper func(d *Domain)) []byte {
+		d := *valid
+		tamper(&d)
+		var buf bytes.Buffer
+		_, err := d.WriteTo(&buf)
+		assert.NoError(err)
+		return buf.Bytes()
+	}
+
+	one := fr.One()
+
+	for _, tc := range []struct {
+		name string
+		data []byte
+	}{
+		{
+			// bits.TrailingZeros64(0) is 64, which used to size the twiddle
+			// allocations at 1<<63 and take the process down.
+			name: "zero cardinality",
+			data: serialize(func(d *Domain) { d.Cardinality = 0 }),
+		}, {
+			name: "cardinality not a power of 2",
+			data: serialize(func(d *Domain) { d.Cardinality = (1 << 6) + 1 }),
+		}, {
+			// beyond the 2-adicity of every supported field
+			name: "cardinality beyond 2-adicity",
+			data: serialize(func(d *Domain) { d.Cardinality = 1 << 63 }),
+		}, {
+			name: "generator does not match cardinality",
+			data: serialize(func(d *Domain) { d.Generator = one }),
+		}, {
+			name: "generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.GeneratorInv = one }),
+		}, {
+			name: "cardinality inverse mismatch",
+			data: serialize(func(d *Domain) { d.CardinalityInv = one }),
+		}, {
+			name: "multiplicative generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.FrMultiplicativeGenInv = one }),
+		}, {
+			// a short read must not decode a zero-padded element
+			name: "truncated element",
+			data: serialize(func(d *Domain) {})[:8+fr.Bytes+fr.Bytes/2],
+		},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			var d Domain
+			_, err := d.ReadFrom(bytes.NewReader(tc.data))
+			assert.Error(err, "invalid domain should be rejected")
+		})
+	}
+}
+
 func TestNewDomainCache(t *testing.T) {
 	t.Run("CacheWithoutShift", func(t *testing.T) {
 		key1 := domainCacheKey{
```

### ecc/bn254/fr/fft/domain.go
```diff
@@ -377,7 +377,15 @@ func (d *Domain) WriteTo(w io.Writer) (int64, error) {
 	return written, nil
 }
 
-// ReadFrom attempts to decode a domain from Reader
+// ReadFrom attempts to decode a domain from Reader.
+//
+// It rejects a cardinality that is not a power of two or that exceeds the
+// field's 2-adicity, and checks the decoded elements for consistency with the
+// cardinality and with one another.
+//
+// It does not impose a resource limit: a cardinality may be valid and still
+// large, and the precomputation it triggers allocates memory linear in the
+// cardinality. Callers decoding untrusted input must bound the size themselves.
 func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 
 	var read int64
@@ -389,21 +397,52 @@ func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 	}
 	read += 8
 
+	// Cardinality must be a non-zero power of 2 within the field's 2-adicity.
+	if d.Cardinality == 0 || bits.OnesCount64(d.Cardinality) != 1 {
+		return read, errors.New("fft: invalid domain cardinality: must be a non-zero power of 2")
+	}
+	// Generator is deterministic in the cardinality, so it doubles as the
+	// 2-adicity bound check and as the expected value for d.Generator below.
+	generator, err := Generator(d.Cardinality)
+	if err != nil {
+		return read, err
+	}
+
 	toDecode := []*fr.Element{&d.CardinalityInv, &d.Generator, &d.GeneratorInv, &d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv}
 
 	for _, v := range toDecode {
 		var buf [fr.Bytes]byte
-		_, err = r.Read(buf[:])
+		// io.Reader may return fewer than len(buf) bytes without an error, so
+		// read the element in full rather than decoding a truncated buffer.
+		n, err := io.ReadFull(r, buf[:])
+		read += int64(n)
 		if err != nil {
 			return read, err
 		}
-		read += fr.Bytes
 		*v, err = fr.BigEndian.Element(&buf)
 		if err != nil {
 			return read, err
 		}
 	}
 
+	// The decoded elements are individually valid field elements; check that
+	// they also describe this domain.
+	if !d.Generator.Equal(&generator) {
+		return read, errors.New("fft: invalid domain: generator does not match cardinality")
+	}
+	var check fr.Element
+	if !check.Mul(&d.Generator, &d.GeneratorInv).IsOne() {
+		return read, errors.New("fft: invalid domain: generator inverse mismatch")
+	}
+	if !check.SetUint64(d.Cardinality).Mul(&check, &d.CardinalityInv).IsOne() {
+		return read, errors.New("fft: invalid domain: cardinality inverse mismatch")
+	}
+	// FrMultiplicativeGen is caller-chosen (see WithShift), so only its inverse
+	// can be checked.
+	if !check.Mul(&d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv).IsOne() {
+		return read, errors.New("fft: invalid domain: multiplicative generator inverse mismatch")
+	}
+
 	err = binary.Read(r, binary.BigEndian, &d.withPrecompute)
 	if err != nil {
 		return read, err
```

### ecc/bn254/fr/fft/domain_test.go
```diff
@@ -39,6 +39,66 @@ func TestDomainSerialization(t *testing.T) {
 	}
 }
 
+func TestDomainDeserializationInvalid(t *testing.T) {
+	assert := require.New(t)
+
+	valid := NewDomain(1 << 6)
+
+	// serialize returns the encoding of d, with the fields of a valid domain
+	// overwritten by tamper.
+	serialize := func(tamper func(d *Domain)) []byte {
+		d := *valid
+		tamper(&d)
+		var buf bytes.Buffer
+		_, err := d.WriteTo(&buf)
+		assert.NoError(err)
+		return buf.Bytes()
+	}
+
+	one := fr.One()
+
+	for _, tc := range []struct {
+		name string
+		data []byte
+	}{
+		{
+			// bits.TrailingZeros64(0) is 64, which used to size the twiddle
+			// allocations at 1<<63 and take the process down.
+			name: "zero cardinality",
+			data: serialize(func(d *Domain) { d.Cardinality = 0 }),
+		}, {
+			name: "cardinality not a power of 2",
+			data: serialize(func(d *Domain) { d.Cardinality = (1 << 6) + 1 }),
+		}, {
+			// beyond the 2-adicity of every supported field
+			name: "cardinality beyond 2-adicity",
+			data: serialize(func(d *Domain) { d.Cardinality = 1 << 63 }),
+		}, {
+			name: "generator does not match cardinality",
+			data: serialize(func(d *Domain) { d.Generator = one }),
+		}, {
+			name: "generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.GeneratorInv = one }),
+		}, {
+			name: "cardinality inverse mismatch",
+			data: serialize(func(d *Domain) { d.CardinalityInv = one }),
+		}, {
+			name: "multiplicative generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.FrMultiplicativeGenInv = one }),
+		}, {
+			// a short read must not decode a zero-padded element
+			name: "truncated element",
+			data: serialize(func(d *Domain) {})[:8+fr.Bytes+fr.Bytes/2],
+		},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			var d Domain
+			_, err := d.ReadFrom(bytes.NewReader(tc.data))
+			assert.Error(err, "invalid domain should be rejected")
+		})
+	}
+}
+
 func TestNewDomainCache(t *testing.T) {
 	t.Run("CacheWithoutShift", func(t *testing.T) {
 		key1 := domainCacheKey{
```

### ecc/bw6-633/fr/fft/domain.go
```diff
@@ -377,7 +377,15 @@ func (d *Domain) WriteTo(w io.Writer) (int64, error) {
 	return written, nil
 }
 
-// ReadFrom attempts to decode a domain from Reader
+// ReadFrom attempts to decode a domain from Reader.
+//
+// It rejects a cardinality that is not a power of two or that exceeds the
+// field's 2-adicity, and checks the decoded elements for consistency with the
+// cardinality and with one another.
+//
+// It does not impose a resource limit: a cardinality may be valid and still
+// large, and the precomputation it triggers allocates memory linear in the
+// cardinality. Callers decoding untrusted input must bound the size themselves.
 func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 
 	var read int64
@@ -389,21 +397,52 @@ func (d *Domain) ReadFrom(r io.Reader) (int64, error) {
 	}
 	read += 8
 
+	// Cardinality must be a non-zero power of 2 within the field's 2-adicity.
+	if d.Cardinality == 0 || bits.OnesCount64(d.Cardinality) != 1 {
+		return read, errors.New("fft: invalid domain cardinality: must be a non-zero power of 2")
+	}
+	// Generator is deterministic in the cardinality, so it doubles as the
+	// 2-adicity bound check and as the expected value for d.Generator below.
+	generator, err := Generator(d.Cardinality)
+	if err != nil {
+		return read, err
+	}
+
 	toDecode := []*fr.Element{&d.CardinalityInv, &d.Generator, &d.GeneratorInv, &d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv}
 
 	for _, v := range toDecode {
 		var buf [fr.Bytes]byte
-		_, err = r.Read(buf[:])
+		// io.Reader may return fewer than len(buf) bytes without an error, so
+		// read the element in full rather than decoding a truncated buffer.
+		n, err := io.ReadFull(r, buf[:])
+		read += int64(n)
 		if err != nil {
 			return read, err
 		}
-		read += fr.Bytes
 		*v, err = fr.BigEndian.Element(&buf)
 		if err != nil {
 			return read, err
 		}
 	}
 
+	// The decoded elements are individually valid field elements; check that
+	// they also describe this domain.
+	if !d.Generator.Equal(&generator) {
+		return read, errors.New("fft: invalid domain: generator does not match cardinality")
+	}
+	var check fr.Element
+	if !check.Mul(&d.Generator, &d.GeneratorInv).IsOne() {
+		return read, errors.New("fft: invalid domain: generator inverse mismatch")
+	}
+	if !check.SetUint64(d.Cardinality).Mul(&check, &d.CardinalityInv).IsOne() {
+		return read, errors.New("fft: invalid domain: cardinality inverse mismatch")
+	}
+	// FrMultiplicativeGen is caller-chosen (see WithShift), so only its inverse
+	// can be checked.
+	if !check.Mul(&d.FrMultiplicativeGen, &d.FrMultiplicativeGenInv).IsOne() {
+		return read, errors.New("fft: invalid domain: multiplicative generator inverse mismatch")
+	}
+
 	err = binary.Read(r, binary.BigEndian, &d.withPrecompute)
 	if err != nil {
 		return read, err
```

### ecc/bw6-633/fr/fft/domain_test.go
```diff
@@ -39,6 +39,66 @@ func TestDomainSerialization(t *testing.T) {
 	}
 }
 
+func TestDomainDeserializationInvalid(t *testing.T) {
+	assert := require.New(t)
+
+	valid := NewDomain(1 << 6)
+
+	// serialize returns the encoding of d, with the fields of a valid domain
+	// overwritten by tamper.
+	serialize := func(tamper func(d *Domain)) []byte {
+		d := *valid
+		tamper(&d)
+		var buf bytes.Buffer
+		_, err := d.WriteTo(&buf)
+		assert.NoError(err)
+		return buf.Bytes()
+	}
+
+	one := fr.One()
+
+	for _, tc := range []struct {
+		name string
+		data []byte
+	}{
+		{
+			// bits.TrailingZeros64(0) is 64, which used to size the twiddle
+			// allocations at 1<<63 and take the process down.
+			name: "zero cardinality",
+			data: serialize(func(d *Domain) { d.Cardinality = 0 }),
+		}, {
+			name: "cardinality not a power of 2",
+			data: serialize(func(d *Domain) { d.Cardinality = (1 << 6) + 1 }),
+		}, {
+			// beyond the 2-adicity of every supported field
+			name: "cardinality beyond 2-adicity",
+			data: serialize(func(d *Domain) { d.Cardinality = 1 << 63 }),
+		}, {
+			name: "generator does not match cardinality",
+			data: serialize(func(d *Domain) { d.Generator = one }),
+		}, {
+			name: "generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.GeneratorInv = one }),
+		}, {
+			name: "cardinality inverse mismatch",
+			data: serialize(func(d *Domain) { d.CardinalityInv = one }),
+		}, {
+			name: "multiplicative generator inverse mismatch",
+			data: serialize(func(d *Domain) { d.FrMultiplicativeGenInv = one }),
+		}, {
+			// a short read must not decode a zero-padded element
+			name: "truncated element",
+			data: serialize(func(d *Domain) {})[:8+fr.Bytes+fr.Bytes/2],
+		},
+	} {
+		t.Run(tc.name, func(t *testing.T) {
+			var d Domain
+			_, err := d.ReadFrom(bytes.NewReader(tc.data))
+			assert.Error(err, "invalid domain should be rejected")
+		})
+	}
+}
+
 func TestNewDomainCache(t *testing.T) {
 	t.Run("CacheWithoutShift", func(t *testing.T) {
 		key1 := domainCacheKey{
```
