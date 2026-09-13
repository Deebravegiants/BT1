# [?] polygon/sync: ignore empty NewBlockHashes to prevent observer panic (#21560)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-02
Source: https://github.com/erigontech/erigon/commit/bae1c116f8e5df9bd2bfe2ef27ce3b60690a8560
Type: security-commit

## Details
polygon/sync: ignore empty NewBlockHashes to prevent observer panic (#21560)

## Summary
An **empty** NewBlockHashes packet (RLP `0xc0`) decodes to a zero-length
slice **without error**, so the surviving `execution/p2p` inbound path
delivers it to observers unpenalized. The `polygon/sync` tip-events
observer then indexed `blockHashes[0]` with no length check and
panicked; observers run in a bare `go observer(event)` with no
`recover()`, so the panic aborted the whole process — a remote,
unauthenticated **crash DoS on polygon/Bor nodes**.

Fix: ignore announcements with no entries before any `blockHashes[0]`
access.

Closes erigontech/security#72

## Scope
Only the polygon/Bor astrid path (`polygon/sync` tip-events) is affected
— it is the live consumer of inbound NewBlockHashes. On post-Merge
Ethereum the eth multi-client drops these messages (#21505), so this is
polygon-specific. `peer_tracker`'s observer ranges over the slice and is
already safe on empty; `NewBlock` decodes into a struct, so an empty
packet is rejected at decode rather than reaching an observer.

## Test plan
- [x] `TestTipEventsEmptyNewBlockHashesDoesNotPanic` — empty packet no
longer panics the observer (red→green; the red failure was `index out of
range [0] with length 0` at `tip_events.go:213`)
- [x] `TestTipEventsNewBlockHashesEmitsEvent` — non-empty announcements
still emit a `NewBlockHashes` event
- [x] `go test -race ./polygon/sync/` (new tests, `-count=5`)
- [x] `make lint` clean; `make erigon integration`

## Note
A `recover()` in `common/event` `Observers.Notify` would be
complementary defense-in-depth — it would catch any future observer
panic, not just this one — but per the issue it should not replace this
targeted length guard.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Co-authored-by: milen <94537774+taratorio@users.noreply.github.com>

### polygon/sync/tip_events.go
```diff
@@ -209,6 +209,10 @@ func (te *TipEvents) Run(ctx context.Context) error {
 
 	newBlockHashesObserverCancel := te.p2pObserverRegistrar.RegisterNewBlockHashesObserver(func(message *p2p.DecodedInboundMessage[*eth.NewBlockHashesPacket]) {
 		blockHashes := *message.Decoded
+		// A peer can send an empty NewBlockHashes packet; skip it to avoid the blockHashes[0] panics below.
+		if len(blockHashes) == 0 {
+			return
+		}
 
 		if te.blockEventsSpamGuard.Spam(message.PeerId, blockHashes[0].Hash, blockHashes[0].Number) {
 			return
```

### polygon/sync/tip_events_empty_newblockhashes_test.go
```diff
@@ -0,0 +1,107 @@
+// Copyright 2026 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+package sync
+
+import (
+	"context"
+	"testing"
+	"time"
+
+	"github.com/stretchr/testify/require"
+	"golang.org/x/sync/errgroup"
+
+	"github.com/erigontech/erigon/common"
+	"github.com/erigontech/erigon/common/event"
+	"github.com/erigontech/erigon/common/log/v3"
+	"github.com/erigontech/erigon/common/testlog"
+	"github.com/erigontech/erigon/execution/p2p"
+	"github.com/erigontech/erigon/execution/types"
+	"github.com/erigontech/erigon/p2p/protocols/eth"
+	"github.com/erigontech/erigon/polygon/heimdall"
+)
+
+type captureNewBlockHashesRegistrar struct {
+	captured chan event.Observer[*p2p.DecodedInboundMessage[*eth.NewBlockHashesPacket]]
+}
+
+func (captureNewBlockHashesRegistrar) RegisterNewBlockObserver(event.Observer[*p2p.DecodedInboundMessage[*eth.NewBlockPacket]]) event.UnregisterFunc {
+	return func() {}
+}
+
+func (c captureNewBlockHashesRegistrar) RegisterNewBlockHashesObserver(o event.Observer[*p2p.DecodedInboundMessage[*eth.NewBlockHashesPacket]]) event.UnregisterFunc {
+	c.captured <- o
+	return func() {}
+}
+
+type noopHeimdallRegistrar struct{}
+
+func (noopHeimdallRegistrar) RegisterMilestoneObserver(func(*heimdall.Milestone), ...heimdall.ObserverOption) event.UnregisterFunc {
+	return func() {}
+}
+
+type noopMinedBlockRegistrar struct{}
+
+func (noopMinedBlockRegistrar) RegisterMinedBlockObserver(func(*types.Block)) event.UnregisterFunc {
+	return func() {}
+}
+
+func runTipEventsCapturingNewBlockHashesObserver(t *testing.T) (event.Observer[*p2p.DecodedInboundMessage[*eth.NewBlockHashesPacket]], *TipEvents) {
+	t.Helper()
+	reg := captureNewBlockHashesRegistrar{captured: make(chan event.Observer[*p2p.DecodedInboundMessage[*eth.NewBlockHashesPacket]], 1)}
+	te := NewTipEvents(testlog.Logger(t, log.LvlCrit), reg, noopHeimdallRegistrar{}, noopMinedBlockRegistrar{})
+	ctx, cancel := context.WithCancel(t.Context())
+	eg := errgroup.Group{}
+	eg.Go(func() error { return te.Run(ctx) })
+	t.Cleanup(func() {
+		cancel()
+		require.ErrorIs(t, eg.Wait(), context.Canceled)
+	})
+
+	select {
+	case obs := <-reg.captured:
+		return obs, te
+	case <-time.After(5 * time.Second):
+		t.Fatal("NewBlockHashes observer was not registered")
+		return nil, nil
+	}
+}
+
+func TestTipEventsEmptyNewBlockHashesDoesNotPanic(t *testing.T) {
+	t.Parallel()
+	obs, _ := runTipEventsCapturingNewBlockHashesObserver(t)
+
+	require.NotPanics(t, func() {
+		obs(&p2p.DecodedInboundMessage[*eth.NewBlockHashesPacket]{
+			Decoded: &eth.NewBlockHashesPacket{},
+			PeerId:  p2p.PeerIdFromUint64(1),
+		})
+	})
+}
+
+func TestTipEventsNewBlockHashesEmitsEvent(t *testing.T) {
+	t.Parallel()
+	obs, te := runTipEventsCapturingNewBlockHashesObserver(t)
+
+	obs(&p2p.DecodedInboundMessage[*eth.NewBlockHashesPacket]{
+		Decoded: &eth.NewBlockHashesPacket{{Hash: common.HexToHash("0x1"), Number: 1}},
+		PeerId:  p2p.PeerIdFromUint64(1),
+	})
+
+	readCtx, cancel := context.WithTimeout(t.Context(), 5*time.Second)
+	defer cancel()
+	require.Equal(t, EventTypeNewBlockHashes, read(readCtx, t, te.Events()).Type)
+}
```
