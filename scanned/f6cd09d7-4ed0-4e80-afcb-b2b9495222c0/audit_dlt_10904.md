# [?] fix(sync): fix potential race condition on accessing cached values

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-02-24
Source: https://github.com/vechain/thor/commit/6dae1187a666c2ac6d0d2fc7ea3893dd44cb96d1
Type: security-commit

## Details
fix(sync): fix potential race condition on accessing cached values

#43

## Patch
### block/block.go
```diff
@@ -3,6 +3,7 @@ package block
 import (
 	"fmt"
 	"io"
+	"sync/atomic"
 
 	"github.com/ethereum/go-ethereum/rlp"
 	"github.com/vechain/thor/tx"
@@ -13,7 +14,7 @@ type Block struct {
 	header *Header
 	txs    tx.Transactions
 	cache  struct {
-		size *int
+		size atomic.Value
 	}
 }
 
@@ -83,10 +84,10 @@ func (b *Block) DecodeRLP(s *rlp.Stream) error {
 
 // Size returns block size in bytes.
 func (b *Block) Size() (size int) {
-	if cached := b.cache.size; cached != nil {
-		return *cached
+	if cached := b.cache.size.Load(); cached != nil {
+		return cached.(int)
 	}
-	defer func() { b.cache.size = &size }()
+	defer func() { b.cache.size.Store(size) }()
 	cw := &counterWriter{}
 	rlp.Encode(cw, b)
 
```

### block/header.go
```diff
@@ -4,6 +4,7 @@ import (
 	"encoding/binary"
 	"fmt"
 	"io"
+	"sync/atomic"
 
 	"github.com/ethereum/go-ethereum/crypto"
 	"github.com/ethereum/go-ethereum/crypto/sha3"
@@ -22,9 +23,9 @@ type Header struct {
 	body headerBody
 
 	cache struct {
-		signingHash *thor.Hash
-		signer      *thor.Address
-		id          *thor.Hash
+		signingHash atomic.Value
+		signer      atomic.Value
+		id          atomic.Value
 	}
 }
 
@@ -118,14 +119,14 @@ func (h *Header) ReceiptsRoot() thor.Hash {
 // The block ID is defined as: blockNumber + hash(signingHash, signer)[4:],
 // and the last byte is the chain tag.
 func (h *Header) ID() (id thor.Hash) {
-	if cached := h.cache.id; cached != nil {
-		return *cached
+	if cached := h.cache.id.Load(); cached != nil {
+		return cached.(thor.Hash)
 	}
 	defer func() {
 		// overwrite first 4 bytes of block hash to block number.
 		binary.BigEndian.PutUint32(id[:], h.Number())
 		id[len(id)-1] = h.ChainTag()
-		h.cache.id = &id
+		h.cache.id.Store(id)
 	}()
 
 	if h.Number() == 0 {
@@ -149,10 +150,10 @@ func (h *Header) ID() (id thor.Hash) {
 
 // SigningHash computes hash of all header fields excluding signature.
 func (h *Header) SigningHash() (hash thor.Hash) {
-	if cached := h.cache.signingHash; cached != nil {
-		return *cached
+	if cached := h.cache.signingHash.Load(); cached != nil {
+		return cached.(thor.Hash)
 	}
-	defer func() { h.cache.signingHash = &hash }()
+	defer func() { h.cache.signingHash.Store(hash) }()
 
 	hw := sha3.NewKeccak256()
 	rlp.Encode(hw, []interface{}{
@@ -186,12 +187,12 @@ func (h *Header) withSignature(sig []byte) *Header {
 
 // Signer extract signer of the block from signature.
 func (h *Header) Signer() (signer thor.Address, err error) {
-	if cached := h.cache.signer; cached != nil {
-		return *cached, nil
+	if cached := h.cache.signer.Load(); cached != nil {
+		return cached.(thor.Address), nil
 	}
 	defer func() {
 		if err == nil {
-			h.cache.signer = &signer
+			h.cache.signer.Store(signer)
 		}
 	}()
 
```

### tx/transaction.go
```diff
@@ -6,6 +6,7 @@ import (
 	"fmt"
 	"io"
 	"math/big"
+	"sync/atomic"
 
 	"github.com/ethereum/go-ethereum/crypto"
 	"github.com/ethereum/go-ethereum/crypto/sha3"
@@ -33,9 +34,9 @@ type Transaction struct {
 	body body
 
 	cache struct {
-		signingHash *thor.Hash
-		signer      *thor.Address
-		id          *thor.Hash
+		signingHash atomic.Value
+		signer      atomic.Value
+		id          atomic.Value
 	}
 }
 
@@ -67,10 +68,10 @@ func (t *Transaction) BlockRef() (br BlockRef) {
 // ID = hash(signingHash, signer).
 // It returns invalidTxID if signer not available.
 func (t *Transaction) ID() (id thor.Hash) {
-	if cached := t.cache.id; cached != nil {
-		return *cached
+	if cached := t.cache.id.Load(); cached != nil {
+		return cached.(thor.Hash)
 	}
-	defer func() { t.cache.id = &id }()
+	defer func() { t.cache.id.Store(id) }()
 
 	signer, err := t.Signer()
 	if err != nil {
@@ -110,10 +111,10 @@ func (t *Transaction) EvaluateWork(signer thor.Address) *big.Int {
 
 // SigningHash returns hash of tx excludes signature.
 func (t *Transaction) SigningHash() (hash thor.Hash) {
-	if cached := t.cache.signingHash; cached != nil {
-		return *cached
+	if cached := t.cache.signingHash.Load(); cached != nil {
+		return cached.(thor.Hash)
 	}
-	defer func() { t.cache.signingHash = &hash }()
+	defer func() { t.cache.signingHash.Store(hash) }()
 
 	hw := sha3.NewKeccak256()
 	rlp.Encode(hw, []interface{}{
@@ -161,12 +162,12 @@ func (t *Transaction) Signature() []byte {
 
 // Signer extract signer of tx from signature.
 func (t *Transaction) Signer() (signer thor.Address, err error) {
-	if cached := t.cache.signer; cached != nil {
-		return *t.cache.signer, nil
+	if cached := t.cache.signer.Load(); cached != nil {
+		return cached.(thor.Address), nil
 	}
 	defer func() {
 		if err == nil {
-			t.cache.signer = &signer
+			t.cache.signer.Store(signer)
 		}
 	}()
 
```
