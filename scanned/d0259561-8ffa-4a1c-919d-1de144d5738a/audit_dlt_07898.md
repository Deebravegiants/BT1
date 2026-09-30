# [?] Merge branch 'dos-fixes' into release/1.16

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2026-01-13
Source: https://github.com/bnb-chain/bsc/commit/abeb78c647e354ed922726a1d719ac7bc64a07e2
Type: security-commit

## Details
Merge branch 'dos-fixes' into release/1.16

## Patch
### core/txpool/errors.go
```diff
@@ -71,4 +71,7 @@ var (
 	// ErrInflightTxLimitReached is returned when the maximum number of in-flight
 	// transactions is reached for specific accounts.
 	ErrInflightTxLimitReached = errors.New("in-flight transaction limit reached for delegated accounts")
+
+	// ErrKZGVerificationError is returned when a KZG proof was not verified correctly.
+	ErrKZGVerificationError = errors.New("KZG verification error")
 )
```

### core/txpool/validation.go
```diff
@@ -193,7 +193,7 @@ func validateBlobSidecarLegacy(sidecar *types.BlobTxSidecar, hashes []common.Has
 	}
 	for i := range sidecar.Blobs {
 		if err := kzg4844.VerifyBlobProof(&sidecar.Blobs[i], sidecar.Commitments[i], sidecar.Proofs[i]); err != nil {
-			return fmt.Errorf("invalid blob %d: %v", i, err)
+			return fmt.Errorf("%w: invalid blob proof: %v", ErrKZGVerificationError, err)
 		}
 	}
 	return nil
@@ -203,7 +203,10 @@ func validateBlobSidecarOsaka(sidecar *types.BlobTxSidecar, hashes []common.Hash
 	if len(sidecar.Proofs) != len(hashes)*kzg4844.CellProofsPerBlob {
 		return fmt.Errorf("invalid number of %d blob proofs expected %d", len(sidecar.Proofs), len(hashes)*kzg4844.CellProofsPerBlob)
 	}
-	return kzg4844.VerifyCellProofs(sidecar.Blobs, sidecar.Commitments, sidecar.Proofs)
+	if err := kzg4844.VerifyCellProofs(sidecar.Blobs, sidecar.Commitments, sidecar.Proofs); err != nil {
+		return fmt.Errorf("%w: %v", ErrKZGVerificationError, err)
+	}
+	return nil
 }
 
 // ValidationOptionsWithState define certain differences between stateful transaction
```

### crypto/ecies/ecies.go
```diff
@@ -290,7 +290,7 @@ func (prv *PrivateKey) Decrypt(c, s1, s2 []byte) (m []byte, err error) {
 	switch c[0] {
 	case 2, 3, 4:
 		rLen = (prv.PublicKey.Curve.Params().BitSize + 7) / 4
-		if len(c) < (rLen + hLen + 1) {
+		if len(c) < (rLen + hLen + params.BlockSize) {
 			return nil, ErrInvalidMessage
 		}
 	default:
```

### eth/fetcher/tx_fetcher.go
```diff
@@ -114,10 +114,11 @@ type txRequest struct {
 // txDelivery is the notification that a batch of transactions have been added
 // to the pool and should be untracked.
 type txDelivery struct {
-	origin string        // Identifier of the peer originating the notification
-	hashes []common.Hash // Batch of transaction hashes having been delivered
-	metas  []txMetadata  // Batch of metadata associated with the delivered hashes
-	direct bool          // Whether this is a direct reply or a broadcast
+	origin    string        // Identifier of the peer originating the notification
+	hashes    []common.Hash // Batch of transaction hashes having been delivered
+	metas     []txMetadata  // Batch of metadata associated with the delivered hashes
+	direct    bool          // Whether this is a direct reply or a broadcast
+	violation error         // Whether we encountered a protocol violation
 }
 
 // txDrop is the notification that a peer has disconnected.
@@ -285,6 +286,7 @@ func (f *TxFetcher) Enqueue(peer string, txs []*types.Transaction, direct bool)
 		knownMeter       = txReplyKnownMeter
 		underpricedMeter = txReplyUnderpricedMeter
 		otherRejectMeter = txReplyOtherRejectMeter
+		violation        error
 	)
 	if !direct {
 		inMeter = txBroadcastInMeter
@@ -331,6 +333,12 @@ func (f *TxFetcher) Enqueue(peer string, txs []*types.Transaction, direct bool)
 			case errors.Is(err, txpool.ErrUnderpriced) || errors.Is(err, txpool.ErrReplaceUnderpriced) || errors.Is(err, txpool.ErrTxGasPriceTooLow):
 				underpriced++
 
+			case errors.Is(err, txpool.ErrKZGVerificationError):
+				// KZG verification failed, terminate transaction processing immediately.
+				// Since KZG verification is computationally expensive, this acts as a
+				// defensive measure against potential DoS attacks.
+				violation = err
+
 			default:
 				otherreject++
 			}
@@ -339,6 +347,11 @@ func (f *TxFetcher) Enqueue(peer string, txs []*types.Transaction, direct bool)
 				kind: batch[j].Type(),
 				size: uint32(batch[j].Size()),
 			})
+			// Terminate the transaction processing if violation is encountered. All
+			// the remaining transactions in response will be silently discarded.
+			if violation != nil {
+				break
+			}
 		}
 		knownMeter.Mark(duplicate)
 		underpricedMeter.Mark(underpriced)
@@ -349,9 +362,13 @@ func (f *TxFetcher) Enqueue(peer string, txs []*types.Transaction, direct bool)
 			time.Sleep(200 * time.Millisecond)
 			log.Debug("Peer delivering stale transactions", "peer", peer, "rejected", otherreject)
 		}
+		// If we encountered a protocol violation, disconnect this peer.
+		if violation != nil {
+			break
+		}
 	}
 	select {
-	case f.cleanup <- &txDelivery{origin: peer, hashes: added, metas: metas, direct: direct}:
+	case f.cleanup <- &txDelivery{origin: peer, hashes: added, metas: metas, direct: direct, violation: violation}:
 		return nil
 	case <-f.quit:
 		return errTerminated
@@ -746,6 +763,11 @@ func (f *TxFetcher) loop() {
 				// Something was delivered, try to reschedule requests
 				f.scheduleFetches(timeoutTimer, timeoutTrigger, nil) // Partial delivery may enable others to deliver too
 			}
+			// If we encountered a protocol violation, disconnect the peer
+			if delivery.violation != nil {
+				log.Warn("Disconnect peer for protocol violation", "peer", delivery.origin, "error", delivery.violation)
+				f.dropPeer(delivery.origin)
+			}
 
 		case drop := <-f.drop:
 			// A peer was dropped, remove all traces of it
```

### eth/fetcher/tx_fetcher_test.go
```diff
@@ -17,6 +17,7 @@
 package fetcher
 
 import (
+	"crypto/sha256"
 	"errors"
 	"math/big"
 	"math/rand"
@@ -28,7 +29,10 @@ import (
 	"github.com/ethereum/go-ethereum/common/mclock"
 	"github.com/ethereum/go-ethereum/core/txpool"
 	"github.com/ethereum/go-ethereum/core/types"
+	"github.com/ethereum/go-ethereum/crypto"
+	"github.com/ethereum/go-ethereum/crypto/kzg4844"
 	"github.com/ethereum/go-ethereum/params"
+	"github.com/holiman/uint256"
 )
 
 var (
@@ -1908,6 +1912,114 @@ func TestTransactionFetcherDropAlternates(t *testing.T) {
 	})
 }
 
+func makeInvalidBlobTx() *types.Transaction {
+	key, _ := crypto.GenerateKey()
+	blob := &kzg4844.Blob{byte(0xa)}
+	commitment, _ := kzg4844.BlobToCommitment(blob)
+	blobHash := kzg4844.CalcBlobHashV1(sha256.New(), &commitment)
+	cellProof, _ := kzg4844.ComputeCellProofs(blob)
+
+	// Mutate the cell proof
+	cellProof[0][0] = 0x0
+
+	blobtx := &types.BlobTx{
+		ChainID:    uint256.MustFromBig(params.MainnetChainConfig.ChainID),
+		Nonce:      0,
+		GasTipCap:  uint256.NewInt(100),
+		GasFeeCap:  uint256.NewInt(200),
+		Gas:        21000,
+		BlobFeeCap: uint256.NewInt(200),
+		BlobHashes: []common.Hash{blobHash},
+		Value:      uint256.NewInt(100),
+		Sidecar:    types.NewBlobTxSidecar(types.BlobSidecarVersion1, []kzg4844.Blob{*blob}, []kzg4844.Commitment{commitment}, cellProof),
+	}
+	return types.MustSignNewTx(key, types.LatestSigner(params.MainnetChainConfig), blobtx)
+}
+
+// This test ensures that the peer will be disconnected for protocol violation
+// and all its internal traces should be removed properly.
+func TestTransactionProtocolViolation(t *testing.T) {
+	//log.SetDefault(log.NewLogger(log.NewTerminalHandlerWithLevel(os.Stderr, log.LevelDebug, true)))
+
+	var (
+		badTx = makeInvalidBlobTx()
+		drop  = make(chan struct{}, 1)
+	)
+	testTransactionFetcherParallel(t, txFetcherTest{
+		init: func() *TxFetcher {
+			return NewTxFetcher(
+				func(common.Hash) bool { return false },
+				func(txs []*types.Transaction) []error {
+					var errs []error
+					for range txs {
+						errs = append(errs, txpool.ErrKZGVerificationError)
+					}
+					return errs
+				},
+				func(a string, b []common.Hash) error {
+					return nil
+				},
+				func(peer string) { drop <- struct{}{} },
+			)
+		},
+		steps: []interface{}{
+			// Initial announcement to get something into the waitlist
+			doTxNotify{
+				peer:   "A",
+				hashes: []common.Hash{testTxs[0].Hash(), badTx.Hash(), testTxs[1].Hash()},
+				types:  []byte{types.LegacyTxType, types.BlobTxType, types.LegacyTxType},
+				sizes:  []uint32{uint32(testTxs[0].Size()), uint32(badTx.Size()), uint32(testTxs[1].Size())},
+			},
+			isWaiting(map[string][]announce{
+				"A": {
+					{testTxs[0].Hash(), types.LegacyTxType, uint32(testTxs[0].Size())},
+					{badTx.Hash(), types.BlobTxType, uint32(badTx.Size())},
+					{testTxs[1].Hash(), types.LegacyTxType, uint32(testTxs[1].Size())},
+				},
+			}),
+			doWait{time: 0, step: true}, // zero time, but the blob fetching should be scheduled
+
+			isWaiting(map[string][]announce{
+				"A": {
+					{testTxs[0].Hash(), types.LegacyTxType, uint32(testTxs[0].Size())},
+					{testTxs[1].Hash(), types.LegacyTxType, uint32(testTxs[1].Size())},
+				},
+			}),
+			isScheduled{
+				tracking: map[string][]announce{
+					"A": {
+						{badTx.Hash(), types.BlobTxType, uint32(badTx.Size())},
+					},
+				},
+				fetching: map[string][]common.Hash{
+					"A": {badTx.Hash()},
+				},
+			},
+
+			doTxEnqueue{
+				peer:   "A",
+				txs:    []*types.Transaction{badTx},
+				direct: true,
+			},
+			// Some internal traces are left and will be cleaned by a following drop
+			// operation.
+			isWaiting(map[string][]announce{
+				"A": {
+					{testTxs[0].Hash(), types.LegacyTxType, uint32(testTxs[0].Size())},
+					{testTxs[1].Hash(), types.LegacyTxType, uint32(testTxs[1].Size())},
+				},
+			}),
+			isScheduled{},
+			doFunc(func() { <-drop }),
+
+			// Simulate the drop operation emitted by the server
+			doDrop("A"),
+			isWaiting(nil),
+			isScheduled{nil, nil, nil},
+		},
+	})
+}
+
 func testTransactionFetcherParallel(t *testing.T, tt txFetcherTest) {
 	t.Parallel()
 	testTransactionFetcher(t, tt)
```

### version/version.go
```diff
@@ -19,6 +19,6 @@ package version
 const (
 	Major = 1        // Major version component of the current release
 	Minor = 16       // Minor version component of the current release
-	Patch = 7        // Patch version component of the current release
+	Patch = 8        // Patch version component of the current release
 	Meta  = "stable" // Version metadata to append to the version string
 )
```
