# [?] [stream] fix the request manager race condition

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-03-17
Source: https://github.com/harmony-one/harmony/commit/8629a6d45e195e70b68212417558925ed8a2f6d0
Type: security-commit

## Details
[stream] fix the request manager race condition

## Patch
### p2p/stream/common/requestmanager/interface_test.go
```diff
@@ -4,6 +4,7 @@ import (
 	"errors"
 	"fmt"
 	"strconv"
+	"sync"
 
 	"github.com/ethereum/go-ethereum/event"
 	"github.com/ethereum/go-ethereum/rlp"
@@ -18,6 +19,8 @@ type testStreamManager struct {
 
 	newStreamFeed event.Feed
 	rmStreamFeed  event.Feed
+
+	lock sync.Mutex
 }
 
 func newTestStreamManager() *testStreamManager {
@@ -27,12 +30,18 @@ func newTestStreamManager() *testStreamManager {
 }
 
 func (sm *testStreamManager) addNewStream(st sttypes.Stream) {
+	sm.lock.Lock()
 	sm.streams[st.ID()] = st
+	sm.lock.Unlock()
+
 	sm.newStreamFeed.Send(streammanager.EvtStreamAdded{Stream: st})
 }
 
 func (sm *testStreamManager) rmStream(stid sttypes.StreamID) {
+	sm.lock.Lock()
 	delete(sm.streams, stid)
+	sm.lock.Unlock()
+
 	sm.rmStreamFeed.Send(streammanager.EvtStreamRemoved{ID: stid})
 }
 
@@ -45,6 +54,9 @@ func (sm *testStreamManager) SubscribeRemoveStreamEvent(ch chan<- streammanager.
 }
 
 func (sm *testStreamManager) GetStreams() []sttypes.Stream {
+	sm.lock.Lock()
+	defer sm.lock.Unlock()
+
 	sts := make([]sttypes.Stream, 0, len(sm.streams))
 
 	for _, st := range sm.streams {
@@ -54,6 +66,9 @@ func (sm *testStreamManager) GetStreams() []sttypes.Stream {
 }
 
 func (sm *testStreamManager) GetStreamByID(id sttypes.StreamID) (sttypes.Stream, bool) {
+	sm.lock.Lock()
+	defer sm.lock.Unlock()
+
 	st, exist := sm.streams[id]
 	return st, exist
 }
```
