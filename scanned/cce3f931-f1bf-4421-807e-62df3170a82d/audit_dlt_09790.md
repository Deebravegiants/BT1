# [?] fix stream resource leak in HandleStream and panic on double close

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2026-02-09
Source: https://github.com/harmony-one/harmony/commit/46d6689b2c1f39a1623a9bd11f1b7d24931fe5f9
Type: security-commit

## Details
fix stream resource leak in HandleStream and panic on double close

## Patch
### p2p/stream/protocols/sync/protocol.go
```diff
@@ -5,6 +5,7 @@ import (
 	"errors"
 	"fmt"
 	"math/rand"
+	"sync"
 	"time"
 
 	"github.com/ethereum/go-ethereum/event"
@@ -13,7 +14,6 @@ import (
 	shardingconfig "github.com/harmony-one/harmony/internal/configs/sharding"
 	"github.com/harmony-one/harmony/internal/utils"
 	"github.com/harmony-one/harmony/p2p"
-	p2p_host "github.com/harmony-one/harmony/p2p"
 	"github.com/harmony-one/harmony/p2p/discovery"
 	"github.com/harmony-one/harmony/p2p/stream/common/ratelimiter"
 	"github.com/harmony-one/harmony/p2p/stream/common/requestmanager"
@@ -58,16 +58,18 @@ type (
 		config Config
 		logger zerolog.Logger
 
-		ctx    context.Context
-		cancel func()
-		closeC chan struct{}
+		ctx       context.Context
+		cancel    func()
+		closeC    chan struct{}
+		closeOnce sync.Once
 	}
 
 	// Config is the sync protocol config
 	Config struct {
 		Chain      engine.ChainReader
-		Host       p2p_host.Host
+		Host       p2p.Host
 		Discovery  discovery.Discovery
+		Schedule   shardingconfig.Schedule
 		ShardID    nodeconfig.ShardID
 		Network    nodeconfig.NetworkType
 		BeaconNode bool
@@ -89,12 +91,13 @@ func NewProtocol(config Config) *Protocol {
 	ctx, cancel := context.WithCancel(context.Background())
 
 	sp := &Protocol{
-		chain:  config.Chain,
-		disc:   config.Discovery,
-		config: config,
-		ctx:    ctx,
-		cancel: cancel,
-		closeC: make(chan struct{}),
+		chain:    config.Chain,
+		schedule: config.Schedule,
+		disc:     config.Discovery,
+		config:   config,
+		ctx:      ctx,
+		cancel:   cancel,
+		closeC:   make(chan struct{}),
 	}
 	smConfig := streammanager.Config{
 		SoftLoCap: config.SmSoftLowCap,
@@ -145,11 +148,13 @@ func (p *Protocol) Start() {
 
 // Close close the protocol
 func (p *Protocol) Close() {
-	p.rl.Close()
-	p.rm.Close()
-	p.sm.Close()
-	p.cancel()
-	close(p.closeC)
+	p.closeOnce.Do(func() {
+		p.rl.Close()
+		p.rm.Close()
+		p.sm.Close()
+		p.cancel()
+		close(p.closeC)
+	})
 }
 
 // ProtoID return the ProtoID of the sync protocol
@@ -222,10 +227,18 @@ func (p *Protocol) HandleStream(raw libp2p_network.Stream, trusted bool) {
 			p.logger.Warn().Err(err).Str("stream ID", string(st.ID())).
 				Msg("failed to add new stream")
 		}
+		// Close the wrapped stream to avoid resource leak
+		if closeErr := st.Close("failed to add stream: "+err.Error(), false); closeErr != nil {
+			p.logger.Warn().Err(closeErr).Str("stream ID", string(st.ID())).
+				Msg("failed to close rejected stream")
+		}
 		return
 	}
 	//to get my ID use raw.Conn().LocalPeer().String()
-	p.logger.Info().Msgf("Connected to %s (%s)", raw.Conn().RemotePeer().String(), st.ProtoID())
+	p.logger.Info().
+		Str("remotePeer", raw.Conn().RemotePeer().String()).
+		Str("protoID", string(st.ProtoID())).
+		Msg("connected to peer")
 	st.run()
 }
 
```
