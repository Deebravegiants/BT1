# [?] upper limit for values to prevent overflow

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-09-18
Source: https://github.com/0xsoniclabs/sonic/commit/809077fca89557b8a020427f1a6e22b54a7d3a93
Type: security-commit

## Details
upper limit for values to prevent overflow

## Patch
### src/event_check/basic_check/basic_check.go
```diff
@@ -2,6 +2,7 @@ package basic_check
 
 import (
 	"errors"
+	"math"
 
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/params"
@@ -37,6 +38,7 @@ var (
 	ErrNotInited      = errors.New("event field is not initialized")
 	ErrZeroTime       = errors.New("event has zero timestamp")
 	ErrNegativeValue  = errors.New("negative value")
+	ErrHugeValue      = errors.New("too big value")
 )
 
 // Check which don't require anything except event
@@ -118,6 +120,10 @@ func (v *Validator) checkInited(e *inter.Event) error {
 	if e.Seq <= 0 || e.Epoch <= 0 || e.Frame <= 0 || e.Lamport <= 0 {
 		return ErrNotInited // it's unsigned, but check for negative in a case if type will change
 	}
+	if e.Seq >= math.MaxInt32/2 || e.Epoch >= math.MaxInt32/2 || e.Frame >= math.MaxInt32/2 || e.Lamport >= math.MaxInt32/2 {
+		return ErrHugeValue
+	}
+
 	if e.ClaimedTime <= 0 {
 		return ErrZeroTime
 	}
```

### src/gossip/packs_downloader/peer_downloader.go
```diff
@@ -2,6 +2,7 @@ package packs_downloader
 
 import (
 	"errors"
+	"math"
 	"time"
 
 	tree "github.com/emirpasic/gods/maps/treemap"
@@ -218,7 +219,7 @@ func (d *PeerPacksDownloader) loop() {
 				log.Error("All the peer packs are unknown. Faulty peer?", "peer", d.peer.Id)
 				d.dropPeer(d.peer.Id)
 			}
-			if packInfo.index == 0 {
+			if packInfo.index <= 0 || packInfo.index >= math.MaxInt32 {
 				log.Error("invalid pack index", "peer", d.peer.Id)
 				continue
 			}
```

### src/poset/frame_info.go
```diff
@@ -2,6 +2,9 @@ package poset
 
 import (
 	"github.com/Fantom-foundation/go-lachesis/src/inter"
+	"github.com/ethereum/go-ethereum/rlp"
+	"io"
+	"math"
 )
 
 // TODO: make FrameInfo internal
@@ -11,6 +14,28 @@ type FrameInfo struct {
 	TimeRatio  inter.Timestamp
 }
 
+type frameInfoMarshaling struct {
+	TimeOffset uint64
+	TimeRatio  inter.Timestamp
+}
+
+func (f *FrameInfo) EncodeRLP(w io.Writer) error {
+	return rlp.Encode(w, frameInfoMarshaling{
+		TimeOffset: uint64(f.TimeOffset + math.MaxInt64/2),
+		TimeRatio:  f.TimeRatio,
+	})
+}
+
+func (f *FrameInfo) DecodeRLP(st *rlp.Stream) error {
+	m := frameInfoMarshaling{}
+	if err := st.Decode(&m); err != nil {
+		return err
+	}
+	f.TimeOffset = int64(m.TimeOffset) - math.MaxInt64/2
+	f.TimeRatio = m.TimeRatio
+	return nil
+}
+
 // GetConsensusTimestamp calc consensus timestamp for given event.
 func (f *FrameInfo) GetConsensusTimestamp(e *Event) inter.Timestamp {
 	return inter.Timestamp(int64(e.Lamport)*int64(f.TimeRatio) + f.TimeOffset)
```

### src/poset/frame_info_test.go
```diff
@@ -3,15 +3,33 @@ package poset
 import (
 	"github.com/ethereum/go-ethereum/rlp"
 	"github.com/stretchr/testify/assert"
+	"math"
 	"testing"
 )
 
 func TestFrameInfoSerialization(t *testing.T) {
 	assertar := assert.New(t)
 
 	f0 := &FrameInfo{
-		TimeOffset: 3,
-		TimeRatio:  1,
+		TimeOffset: math.MaxInt64 / 2,
+		TimeRatio:  math.MaxUint64,
+	}
+	buf, err := rlp.EncodeToBytes(f0)
+	assertar.NoError(err)
+
+	f1 := &FrameInfo{}
+	err = rlp.DecodeBytes(buf, f1)
+	assertar.NoError(err)
+
+	assertar.EqualValues(f0, f1)
+}
+
+func TestFrameInfoSerializationSigned(t *testing.T) {
+	assertar := assert.New(t)
+
+	f0 := &FrameInfo{
+		TimeOffset: -math.MaxInt64 / 2,
+		TimeRatio:  0,
 	}
 	buf, err := rlp.EncodeToBytes(f0)
 	assertar.NoError(err)
```
