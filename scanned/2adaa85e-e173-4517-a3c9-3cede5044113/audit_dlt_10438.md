# [?] Fix data race in downloader (#1961)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2022-10-07
Source: https://github.com/celo-org/celo-blockchain/commit/fb462b6a037d8ffdf20171afbdbc0df41c4ada5d
Type: security-commit

## Details
Fix data race in downloader (#1961)

* chore: Fix some typos

* downloader: Fix data race when fetching headers

* downloaded: Cache extra data error as well

## Patch
### consensus/consensustest/mockprotocol.go
```diff
@@ -228,7 +228,7 @@ func (e *MockEngine) VerifyHeader(chain consensus.ChainHeaderReader, header *typ
 // verifyHeader checks whether a header conforms to the consensus rules
 func (e *MockEngine) verifyHeader(chain consensus.ChainHeaderReader, header, parent *types.Header, seal bool) error {
 	// Ensure that the extra data format is satisfied
-	if _, err := types.ExtractIstanbulExtra(header); err != nil {
+	if _, err := header.IstanbulExtra(); err != nil {
 		return errors.New("invalid extra data format")
 	}
 	// Verify the header's timestamp
```

### consensus/istanbul/backend/backend.go
```diff
@@ -476,7 +476,7 @@ func (sb *Backend) ParentBlockValidators(proposal istanbul.Proposal) istanbul.Va
 }
 
 func (sb *Backend) NextBlockValidators(proposal istanbul.Proposal) (istanbul.ValidatorSet, error) {
-	istExtra, err := types.ExtractIstanbulExtra(proposal.Header())
+	istExtra, err := proposal.Header().IstanbulExtra()
 	if err != nil {
 		return nil, err
 	}
@@ -650,7 +650,7 @@ func (sb *Backend) verifyValSetDiff(proposal istanbul.Proposal, block *types.Blo
 	header := block.Header()
 
 	// Ensure that the extra data format is satisfied
-	istExtra, err := types.ExtractIstanbulExtra(header)
+	istExtra, err := header.IstanbulExtra()
 	if err != nil {
 		return err
 	}
@@ -806,7 +806,7 @@ func (sb *Backend) GetCurrentHeadBlockAndAuthor() (istanbul.Proposal, common.Add
 
 func (sb *Backend) LastSubject() (istanbul.Subject, error) {
 	lastProposal, _ := sb.GetCurrentHeadBlockAndAuthor()
-	istExtra, err := types.ExtractIstanbulExtra(lastProposal.Header())
+	istExtra, err := lastProposal.Header().IstanbulExtra()
 	if err != nil {
 		return istanbul.Subject{}, err
 	}
```

### consensus/istanbul/backend/engine.go
```diff
@@ -138,7 +138,7 @@ func (sb *Backend) verifyHeader(chain consensus.ChainHeaderReader, header *types
 	}
 
 	// Ensure that the extra data format is satisfied
-	if _, err := types.ExtractIstanbulExtra(header); err != nil {
+	if _, err := header.IstanbulExtra(); err != nil {
 		return errInvalidExtraDataFormat
 	}
 
@@ -273,7 +273,7 @@ func (sb *Backend) verifyAggregatedSeals(chain consensus.ChainHeaderReader, head
 		return nil
 	}
 
-	extra, err := types.ExtractIstanbulExtra(header)
+	extra, err := header.IstanbulExtra()
 	if err != nil {
 		return err
 	}
@@ -373,7 +373,7 @@ func (sb *Backend) VerifySeal(header *types.Header) error {
 		return errUnknownBlock
 	}
 
-	extra, err := types.ExtractIstanbulExtra(header)
+	extra, err := header.IstanbulExtra()
 	if err != nil {
 		return errInvalidExtraDataFormat
 	}
@@ -861,7 +861,7 @@ func (sb *Backend) snapshot(chain consensus.ChainHeaderReader, number uint64, ha
 			return nil, errors.New("Cannot load genesis")
 		}
 
-		istanbulExtra, err := types.ExtractIstanbulExtra(genesis)
+		istanbulExtra, err := genesis.IstanbulExtra()
 		if err != nil {
 			log.Error("Unable to extract istanbul extra", "err", err)
 			return nil, err
@@ -948,7 +948,7 @@ func (sb *Backend) addParentSeal(chain consensus.ChainHeaderReader, header *type
 
 	// Get parent's extra to fetch it's AggregatedSeal
 	parent := chain.GetHeader(header.ParentHash, number-1)
-	parentExtra, err := types.ExtractIstanbulExtra(parent)
+	parentExtra, err := parent.IstanbulExtra()
 	if err != nil {
 		return err
 	}
@@ -1046,7 +1046,7 @@ func ecrecover(header *types.Header) (common.Address, error) {
 	}
 
 	// Retrieve the signature from the header extra-data
-	istanbulExtra, err := types.ExtractIstanbulExtra(header)
+	istanbulExtra, err := header.IstanbulExtra()
 	if err != nil {
 		return common.Address{}, err
 	}
@@ -1099,7 +1099,7 @@ func writeValidatorSetDiff(header *types.Header, oldValSet []istanbul.ValidatorD
 			"addedValidators", common.ConvertToStringSlice(addedValidatorsAddresses), "removedValidators", removedValidators.Text(16))
 	}
 
-	extra, err := types.ExtractIstanbulExtra(header)
+	extra, err := header.IstanbulExtra()
 	if err != nil {
 		return nil
 	}
@@ -1124,7 +1124,7 @@ func writeSeal(h *types.Header, seal []byte) error {
 		return errInvalidSignature
 	}
 
-	istanbulExtra, err := types.ExtractIstanbulExtra(h)
+	istanbulExtra, err := h.IstanbulExtra()
 	if err != nil {
 		return err
 	}
@@ -1147,7 +1147,7 @@ func writeAggregatedSeal(h *types.Header, aggregatedSeal types.IstanbulAggregate
 		return errInvalidAggregatedSeal
 	}
 
-	istanbulExtra, err := types.ExtractIstanbulExtra(h)
+	istanbulExtra, err := h.IstanbulExtra()
 	if err != nil {
 		return err
 	}
```

### consensus/istanbul/backend/engine_test.go
```diff
@@ -177,7 +177,7 @@ func TestVerifySeal(t *testing.T) {
 
 	// modify seal bitmap and expect to fail the quorum check
 	header = block.Header()
-	extra, err := types.ExtractIstanbulExtra(header)
+	extra, err := header.IstanbulExtra()
 	g.Expect(err).ToNot(HaveOccurred())
 	extra.AggregatedSeal.Bitmap = big.NewInt(0)
 	encoded, err := rlp.EncodeToBytes(extra)
@@ -357,7 +357,7 @@ func TestPrepareExtra(t *testing.T) {
 	g.Expect(err).ToNot(HaveOccurred())
 
 	// the header must have the updated extra data
-	updatedExtra, err := types.ExtractIstanbulExtra(h)
+	updatedExtra, err := h.IstanbulExtra()
 	g.Expect(err).ToNot(HaveOccurred())
 
 	var updatedExtraVals []istanbul.ValidatorData
@@ -407,7 +407,7 @@ func TestWriteSeal(t *testing.T) {
 	g.Expect(err).NotTo(HaveOccurred())
 
 	// verify istanbul extra-data
-	actualIstExtra, err := types.ExtractIstanbulExtra(h)
+	actualIstExtra, err := h.IstanbulExtra()
 	g.Expect(err).NotTo(HaveOccurred())
 	g.Expect(actualIstExtra).To(Equal(expectedIstExtra))
 
@@ -457,7 +457,7 @@ func TestWriteAggregatedSeal(t *testing.T) {
 	g.Expect(err).NotTo(HaveOccurred())
 
 	// verify istanbul extra-data
-	actualIstExtra, err := types.ExtractIstanbulExtra(h)
+	actualIstExtra, err := h.IstanbulExtra()
 	g.Expect(err).NotTo(HaveOccurred())
 	g.Expect(actualIstExtra).To(Equal(expectedIstExtra))
 
```

### consensus/istanbul/backend/handler.go
```diff
@@ -239,7 +239,7 @@ func (sb *Backend) UpdateMetricsForParentOfBlock(child *types.Block) {
 
 	// Now check if this validator signer is in the "parent seal" on the child block.
 	// The parent seal is used for downtime calculations.
-	childExtra, err := types.ExtractIstanbulExtra(child.Header())
+	childExtra, err := child.Header().IstanbulExtra()
 	if err != nil {
 		return
 	}
```

### consensus/istanbul/backend/snapshot.go
```diff
@@ -130,7 +130,7 @@ func (s *Snapshot) apply(headers []*types.Header, db ethdb.Database) (*Snapshot,
 		}
 
 		// Ensure that the extra data format is satisfied
-		istExtra, err := types.ExtractIstanbulExtra(header)
+		istExtra, err := header.IstanbulExtra()
 		if err != nil {
 			log.Error("Unable to extract the istanbul extra field from the header", "header", header)
 			return nil, err
```

### consensus/istanbul/uptime/monitor.go
```diff
@@ -150,7 +150,7 @@ func (um *Monitor) ProcessHeader(header *types.Header) error {
 	}
 
 	// Get the bitmap from the previous block
-	extra, err := types.ExtractIstanbulExtra(header)
+	extra, err := header.IstanbulExtra()
 	if err != nil {
 		um.logger.Error("Unable to extract istanbul extra", "func", "ProcessBlock", "blocknum", headerNumber)
 		return errors.New("could not extract block header extra")
```

### core/types/block.go
```diff
@@ -23,6 +23,7 @@ import (
 	"io"
 	"math/big"
 	"reflect"
+	"sync"
 	"sync/atomic"
 	"time"
 
@@ -52,6 +53,11 @@ type Header struct {
 	GasUsed     uint64         `json:"gasUsed"          gencodec:"required"`
 	Time        uint64         `json:"timestamp"        gencodec:"required"`
 	Extra       []byte         `json:"extraData"        gencodec:"required"`
+
+	// Used to cache deserialized istanbul extra data
+	extraLock  sync.Mutex
+	extraValue *IstanbulExtra
+	extraError error
 }
 
 // field type overrides for gencodec
@@ -100,6 +106,10 @@ func (h *Header) SanityCheck() error {
 // EmptyBody returns true if there is no additional 'body' to complete the header
 // that is: no transactions.
 func (h *Header) EmptyBody() bool {
+	if _, err := h.IstanbulExtra(); err == nil {
+		return false
+	}
+
 	return h.TxHash == EmptyRootHash
 }
 
@@ -271,8 +281,19 @@ func NewBlockWithHeader(header *Header) *Block {
 // CopyHeader creates a deep copy of a block header to prevent side effects from
 // modifying a header variable.
 func CopyHeader(h *Header) *Header {
-	cpy := *h
-	if cpy.Number = new(big.Int); h.Number != nil {
+	cpy := Header{
+		ParentHash:  h.ParentHash,
+		Coinbase:    h.Coinbase,
+		Root:        h.Root,
+		TxHash:      h.TxHash,
+		ReceiptHash: h.ReceiptHash,
+		Bloom:       h.Bloom,
+		Number:      new(big.Int),
+		GasUsed:     h.GasUsed,
+		Time:        h.Time,
+	}
+
+	if h.Number != nil {
 		cpy.Number.Set(h.Number)
 	}
 	if len(h.Extra) > 0 {
@@ -366,10 +387,10 @@ func (c *writeCounter) Write(b []byte) (int, error) {
 // WithHeader returns a new block with the data from b but the header replaced with
 // the sealed one.
 func (b *Block) WithHeader(header *Header) *Block {
-	cpy := *header
+	cpy := CopyHeader(header)
 
 	return &Block{
-		header:         &cpy,
+		header:         cpy,
 		transactions:   b.transactions,
 		randomness:     b.randomness,
 		epochSnarkData: b.epochSnarkData,
```

### core/types/celo_additions.go
```diff
@@ -0,0 +1,18 @@
+package types
+
+// IstanbulExtra returns the 'Extra' field of the header deserialized into an
+// IstanbulExtra struct, if there is an error deserializing the 'Extra' field
+// it will be returned.
+func (h *Header) IstanbulExtra() (*IstanbulExtra, error) {
+	h.extraLock.Lock()
+	defer h.extraLock.Unlock()
+
+	if h.extraValue == nil && h.extraError == nil {
+		extra, err := extractIstanbulExtra(h)
+
+		h.extraValue = extra
+		h.extraError = err
+	}
+
+	return h.extraValue, h.extraError
+}
```

### core/types/istanbul.go
```diff
@@ -128,7 +128,7 @@ func (ist *IstanbulExtra) DecodeRLP(s *rlp.Stream) error {
 // ExtractIstanbulExtra extracts all values of the IstanbulExtra from the header. It returns an
 // error if the length of the given extra-data is less than 32 bytes or the extra-data can not
 // be decoded.
-func ExtractIstanbulExtra(h *Header) (*IstanbulExtra, error) {
+func extractIstanbulExtra(h *Header) (*IstanbulExtra, error) {
 	if len(h.Extra) < IstanbulExtraVanity {
 		return nil, ErrInvalidIstanbulHeaderExtra
 	}
@@ -146,7 +146,7 @@ func ExtractIstanbulExtra(h *Header) (*IstanbulExtra, error) {
 // decoded/encoded by rlp.
 func IstanbulFilteredHeader(h *Header, keepSeal bool) *Header {
 	newHeader := CopyHeader(h)
-	istanbulExtra, err := ExtractIstanbulExtra(newHeader)
+	istanbulExtra, err := extractIstanbulExtra(newHeader)
 	if err != nil {
 		return nil
 	}
```

### core/types/istanbul_test.go
```diff
@@ -82,7 +82,7 @@ func TestExtractToIstanbul(t *testing.T) {
 	for _, test := range testCases {
 		h := &Header{Extra: append(test.vanity, test.istRawData...)}
 
-		istanbulExtra, err := ExtractIstanbulExtra(h)
+		istanbulExtra, err := h.IstanbulExtra()
 		if err != test.expectedErr {
 			t.Errorf("expected: %v, but got: %v", test.expectedErr, err)
 		}
```

### core/vm/contracts.go
```diff
@@ -1222,7 +1222,7 @@ func (c *getParentSealBitmap) Run(input []byte, caller common.Address, evm *EVM)
 		return nil, ErrUnexpected
 	}
 
-	extra, err := types.ExtractIstanbulExtra(header)
+	extra, err := header.IstanbulExtra()
 	if err != nil {
 		log.Error("Header without Istanbul extra data encountered in getParentSealBitmap precompile", "blockNumber", blockNumber, "err", err)
 		return nil, ErrEngineIncompatible
@@ -1252,7 +1252,7 @@ func (c *getVerifiedSealBitmap) Run(input []byte, caller common.Address, evm *EV
 	}
 
 	// Extract the verified seal from the header.
-	extra, err := types.ExtractIstanbulExtra(&header)
+	extra, err := header.IstanbulExtra()
 	if err != nil {
 		log.Error("Header without Istanbul extra data encountered in getVerifiedSealBitmap precompile", "extraData", header.Extra, "err", err)
 		// Seal verified by a non-Istanbul engine. Return an error.
```
