# [?] fix(flowrate): fix non-determinism in flowrate tests (#2147)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-02-06
Source: https://github.com/cometbft/cometbft/commit/075d3b594a01ea58fe4ab0b9ea297fe9fe18fff4
Type: security-commit

## Details
fix(flowrate): fix non-determinism in flowrate tests (#2147)

This PR addresses test reliability issues in testreader and testwriter. 

From: #1954 


---

#### PR checklist

- [ ] Tests written/updated
- [ ] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [ ] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

---------

Co-authored-by: Anton Kaliaev <anton.kalyaev@gmail.com>

## Patch
### internal/flowrate/io_test.go
```diff
@@ -99,96 +99,125 @@ func TestReader(t *testing.T) {
 	}
 }
 
+// TestWriter tests the behavior of the Writer in the flowrate package.
+// It verifies that the Writer correctly implements the Limiter interface,
+// and that it correctly reports its status after writing data.
 func TestWriter(t *testing.T) {
-	b := make([]byte, 100)
+	const bufferSize = 100
+	const limit = 200
+	const writeSize = 20
+	const remainingSize = 80
+	const transferSize = 100
+
+	// Initialize a buffer with sequential bytes
+	b := make([]byte, bufferSize)
 	for i := range b {
 		b[i] = byte(i)
 	}
-	w := NewWriter(&bytes.Buffer{}, 200)
-	start := time.Now()
 
-	// Make sure w implements Limiter
-	_ = Limiter(w)
-
-	// Non-blocking 20-byte write for the first sample returns ErrLimit
-	w.SetBlocking(false)
-	if n, err := w.Write(b); n != 20 || err != ErrLimit {
-		t.Fatalf("w.Write(b) expected 20 (ErrLimit); got %v (%v)", n, err)
-	} else if rt := time.Since(start); rt > _50ms {
-		t.Fatalf("w.Write(b) took too long (%v)", rt)
-	}
+	// Create a new Writer with a limit of 200 bytes per second
+	w := NewWriter(&bytes.Buffer{}, limit)
+	start := time.Now()
 
-	// Blocking 80-byte write
-	w.SetBlocking(true)
-	if n, err := w.Write(b[20:]); n != 80 || err != nil {
-		t.Fatalf("w.Write(b[20:]) expected 80 (<nil>); got %v (%v)", n, err)
-	} else if rt := time.Since(start); rt < _300ms {
-		// Explanation for `rt < _300ms` (as opposed to `< _400ms`)
+	// Subtest to verify that the Writer implements the Limiter interface
+	t.Run("implements limiter interface", func(t *testing.T) {
+		_, ok := interface{}(w).(Limiter)
+		if !ok {
+			t.Fatalf("Expected Writer to implement Limiter interface")
+		}
+	})
+
+	// Subtest for non-blocking write
+	t.Run("non-blocking write", func(t *testing.T) {
+		w.SetBlocking(false)
+		n, err := w.Write(b)
+		if n != writeSize || err != ErrLimit {
+			t.Fatalf("w.Write(b) expected %d (ErrLimit); got %v (%v)", writeSize, n, err)
+		}
+		if rt := time.Since(start); rt > _50ms {
+			t.Fatalf("w.Write(b) took too long (%v)", rt)
+		}
+	})
+
+	// Subtest for blocking write
+	t.Run("blocking write", func(t *testing.T) {
+		w.SetBlocking(true)
+		n, err := w.Write(b[writeSize:])
+		if n != remainingSize || err != nil {
+			t.Fatalf("w.Write(b[%d:]) expected %d (<nil>); got %v (%v)", writeSize, remainingSize, n, err)
+		}
+		// Explanation for `rt < _300ms` (as opposed to `< _500ms`)
+		//
+		//	|<-- start        |        |        |
 		//
-		//                 |<-- start        |        |
-		// epochs: -----0ms|---100ms|---200ms|---300ms|---400ms
-		// sends:        20|20      |20      |20      |20#
+		// epochs: -----0ms|---100ms|---200ms|---300ms|---400ms|---500ms
+		// sends:        20|20      |20      |20      |20      |20#
 		//
-		// NOTE: The '#' symbol can thus happen before 400ms is up.
+		// NOTE: The '#' symbol can thus happen before 500ms is up.
 		// Thus, we can only panic if rt < _300ms.
-		t.Fatalf("w.Write(b[20:]) returned ahead of time (%v)", rt)
-	}
-
-	w.SetTransferSize(100)
-	status := []Status{w.Status(), nextStatus(w.Monitor)}
-	start = status[0].Start
+		if rt := time.Since(start); rt < _300ms || rt > _500ms {
+			t.Fatalf("w.Write(b[%d:]) returned at unexpected time (%v)", writeSize, rt)
+		}
+	})
+
+	// Subtest for setting transfer size
+	t.Run("setting transfer size", func(t *testing.T) {
+		w.SetTransferSize(transferSize)
+		status := []Status{w.Status(), nextStatus(w.Monitor)}
+		start = status[0].Start
+
+		// Define expected statuses
+		want := []Status{
+			{start, remainingSize, 4, limit, limit, limit, limit, writeSize, _400ms, 0, _100ms, 80000, true},
+			{start, bufferSize, 5, limit, limit, limit, limit, 0, _500ms, _100ms, 0, 100000, true},
+		}
 
-	// Active, Bytes, Samples, InstRate, CurRate, AvgRate, PeakRate, BytesRem, Start, Duration, Idle, TimeRem, Progress
-	want := []Status{
-		{start, 80, 4, 200, 200, 200, 200, 20, _400ms, 0, _100ms, 80000, true},
-		{start, 100, 5, 200, 200, 200, 200, 0, _500ms, _100ms, 0, 100000, true},
-	}
+		// Compare actual and expected statuses
+		for i, s := range status {
+			if !statusesAreEqual(&s, &want[i]) {
+				t.Errorf("w.Status(%v)\nexpected: %v\ngot     : %v\n", i, want[i], s)
+			}
+		}
+	})
 
-	for i, s := range status {
-		s := s
-		if !statusesAreEqual(&s, &want[i]) {
-			t.Errorf("w.Status(%v)\nexpected: %v\ngot     : %v\n", i, want[i], s)
+	// Subtest to verify that the written data matches the input
+	t.Run("written data matches input", func(t *testing.T) {
+		if !bytes.Equal(b, w.Writer.(*bytes.Buffer).Bytes()) {
+			t.Errorf("w.Write() input doesn't match output")
 		}
-	}
-	if !bytes.Equal(b, w.Writer.(*bytes.Buffer).Bytes()) {
-		t.Errorf("w.Write() input doesn't match output")
-	}
+	})
 }
 
-const (
-	maxDeviationForDuration       = 50 * time.Millisecond
-	maxDeviationForRate     int64 = 50
-)
-
 // statusesAreEqual returns true if s1 is equal to s2. Equality here means
 // general equality of fields except for the duration and rates, which can
 // drift due to unpredictable delays (e.g. thread wakes up 25ms after
 // `time.Sleep` has ended).
 func statusesAreEqual(s1 *Status, s2 *Status) bool {
 	if s1.Active == s2.Active &&
 		s1.Start == s2.Start &&
-		durationsAreEqual(s1.Duration, s2.Duration, maxDeviationForDuration) &&
-		s1.Idle == s2.Idle &&
+		durationsAreEqual(s1.Duration, s2.Duration) &&
+		durationsAreEqual(s1.Idle, s2.Idle) &&
 		s1.Bytes == s2.Bytes &&
 		s1.Samples == s2.Samples &&
 		ratesAreEqual(s1.InstRate, s2.InstRate) &&
 		ratesAreEqual(s1.CurRate, s2.CurRate) &&
 		ratesAreEqual(s1.AvgRate, s2.AvgRate) &&
 		ratesAreEqual(s1.PeakRate, s2.PeakRate) &&
 		s1.BytesRem == s2.BytesRem &&
-		durationsAreEqual(s1.TimeRem, s2.TimeRem, maxDeviationForDuration) &&
+		durationsAreEqual(s1.TimeRem, s2.TimeRem) &&
 		s1.Progress == s2.Progress {
 		return true
 	}
 	return false
 }
 
-func durationsAreEqual(d1 time.Duration, d2 time.Duration, maxDeviation time.Duration) bool {
+func durationsAreEqual(d1 time.Duration, d2 time.Duration) bool {
+	const maxDeviation = 50 * time.Millisecond
 	return d2-d1 <= maxDeviation
 }
 
 func ratesAreEqual(r1 int64, r2 int64) bool {
-	maxDeviation := int64(50)
+	const maxDeviation = int64(50)
 	sub := r1 - r2
 	if sub < 0 {
 		sub = -sub
```
