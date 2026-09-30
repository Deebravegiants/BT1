# [?] Fix data race: istLogger (#1655)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-08-12
Source: https://github.com/celo-org/celo-blockchain/commit/147571e5b5aab36b6de4d839a3ee9c1f85dbd94b
Type: security-commit

## Details
Fix data race: istLogger (#1655)

* Use local logger instead of core logger

* Remove istLogger

## Patch
### consensus/istanbul/backend/backend.go
```diff
@@ -149,20 +149,10 @@ func New(config *istanbul.Config, db ethdb.Database) consensus.Istanbul {
 				"cycle", "sleep", "consensus", "block_verify", "block_construct",
 				"sysload", "syswait", "procload")
 		}
-
 	}
 
 	backend.core = istanbulCore.New(backend, backend.config)
 
-	backend.logger = istanbul.NewIstLogger(
-		func() *big.Int {
-			if backend.core != nil && backend.core.CurrentView() != nil {
-				return backend.core.CurrentView().Round
-			}
-			return common.Big0
-		},
-	)
-
 	if config.Validator {
 		rs, err := replica.NewState(config.Replica, config.ReplicaStateDBPath, backend.StartValidating, backend.StopValidating)
 		if err != nil {
```

### consensus/istanbul/core/core.go
```diff
@@ -180,14 +180,6 @@ func New(backend CoreBackend, config *istanbul.Config) Engine {
 		}, c.checkMessage)
 	c.backlog = msgBacklog
 	c.validateFn = c.checkValidatorSignature
-	c.logger = istanbul.NewIstLogger(
-		func() *big.Int {
-			if c != nil && c.current != nil {
-				return c.current.Round()
-			}
-			return common.Big0
-		},
-	)
 	return c
 }
 
```

### consensus/istanbul/core/handler.go
```diff
@@ -93,9 +93,7 @@ func (c *core) unsubscribeEvents() {
 
 func (c *core) handleEvents() {
 	// Clear state
-	defer func() {
-		c.handlerWg.Done()
-	}()
+	defer c.handlerWg.Done()
 
 	c.handlerWg.Add(1)
 
```

### consensus/istanbul/logger.go
```diff
@@ -1,81 +0,0 @@
-// Copyright 2017 The celo Authors
-// This file is part of the celo library.
-//
-// The celo library is free software: you can redistribute it and/or modify
-// it under the terms of the GNU Lesser General Public License as published by
-// the Free Software Foundation, either version 3 of the License, or
-// (at your option) any later version.
-//
-// The celo library is distributed in the hope that it will be useful,
-// but WITHOUT ANY WARRANTY; without even the implied warranty of
-// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
-// GNU Lesser General Public License for more details.
-//
-// You should have received a copy of the GNU Lesser General Public License
-// along with the celo library. If not, see <http://www.gnu.org/licenses/>.
-
-package istanbul
-
-import (
-	"math/big"
-
-	"github.com/celo-org/celo-blockchain/common"
-	"github.com/celo-org/celo-blockchain/log"
-)
-
-type istLogger struct {
-	logger log.Logger
-	round  func() *big.Int
-}
-
-// NewIstLogger creates an Istanbul Logger with custom logic for exposing logs
-func NewIstLogger(fn func() *big.Int, ctx ...interface{}) log.Logger {
-	return &istLogger{logger: log.New(ctx...), round: fn}
-}
-
-func (l *istLogger) New(ctx ...interface{}) log.Logger {
-	childLogger := l.logger.New(ctx...)
-	return &istLogger{logger: childLogger, round: l.round}
-}
-
-func (l *istLogger) Trace(msg string, ctx ...interface{}) {
-	// If the current round > 1, then upgrade this message to Info
-	if l.round != nil && l.round() != nil && l.round().Cmp(common.Big1) > 0 {
-		l.Info(msg, ctx...)
-	} else {
-		l.logger.Trace(msg, ctx...)
-	}
-}
-
-func (l *istLogger) Debug(msg string, ctx ...interface{}) {
-	// If the current round > 1, then upgrade this message to Info
-	if l.round != nil && l.round() != nil && l.round().Cmp(common.Big1) > 0 {
-		l.Info(msg, ctx...)
-	} else {
-		l.logger.Debug(msg, ctx...)
-	}
-}
-
-func (l *istLogger) Info(msg string, ctx ...interface{}) {
-	l.logger.Info(msg, ctx...)
-}
-
-func (l *istLogger) Warn(msg string, ctx ...interface{}) {
-	l.logger.Warn(msg, ctx...)
-}
-
-func (l *istLogger) Error(msg string, ctx ...interface{}) {
-	l.logger.Error(msg, ctx...)
-}
-
-func (l *istLogger) Crit(msg string, ctx ...interface{}) {
-	l.logger.Crit(msg, ctx...)
-}
-
-func (l *istLogger) GetHandler() log.Handler {
-	return l.logger.GetHandler()
-}
-
-func (l *istLogger) SetHandler(h log.Handler) {
-	l.logger.SetHandler(h)
-}
```

### mobile/geth.go
```diff
@@ -323,7 +323,7 @@ func (n *Node) GetNodeInfo() *NodeInfo {
 	return &NodeInfo{n.node.Server().NodeInfo()}
 }
 
-// GetPeersInfo returns an array of metadata objects describing connected peers.
+// GetPeerInfos returns an array of metadata objects describing connected peers.
 func (n *Node) GetPeerInfos() *PeerInfos {
 	return &PeerInfos{n.node.Server().PeersInfo()}
 }
```
