# [?] p2p: prevent node panic via specially crafted p2p message

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-08-02
Source: https://github.com/kaiachain/kaia/commit/67e5409c945f7efa7bfcabebbae696089c9a46a1
Type: security-commit

## Details
p2p: prevent node panic via specially crafted p2p message

Co-authored-by: Joseph Noh <jiseong.noh@gmail.com>

## Patch
### networks/p2p/peer_error.go
```diff
@@ -54,6 +54,7 @@ func (pe *peerError) Error() string {
 
 var errProtocolReturned = errors.New("protocol returned")
 
+// TODO-klaytn: update the type to uint8
 type DiscReason uint
 
 const (
@@ -89,7 +90,7 @@ var discReasonToString = [...]string{
 }
 
 func (d DiscReason) String() string {
-	if len(discReasonToString) < int(d) {
+	if uint(len(discReasonToString)) < uint(d)  {
 		return fmt.Sprintf("unknown disconnect reason %d", d)
 	}
 	return discReasonToString[d]
```

### networks/p2p/peer_test.go
```diff
@@ -23,11 +23,14 @@ package p2p
 import (
 	"errors"
 	"fmt"
+	"math"
 	"math/rand"
 	"net"
 	"reflect"
 	"testing"
 	"time"
+
+	"github.com/stretchr/testify/assert"
 )
 
 var discard = Protocol{
@@ -167,18 +170,19 @@ func TestPeerPing(t *testing.T) {
 }
 
 func TestPeerDisconnect(t *testing.T) {
-	closer, rw, _, disc := testPeer(nil)
-	defer closer()
-	if err := SendItems(rw, discMsg, DiscQuitting); err != nil {
-		t.Fatal(err)
-	}
-	select {
-	case reason := <-disc:
-		if reason != DiscQuitting {
-			t.Errorf("run returned wrong reason: got %v, want %v", reason, DiscQuitting)
+	testData := []DiscReason{DiscQuitting, math.MaxUint}
+	for _, tc := range testData {
+		closer, rw, _, disc := testPeer(nil)
+		if err := SendItems(rw, discMsg, tc); err != nil {
+			t.Fatal(err)
+		}
+		select {
+		case reason := <-disc:
+			assert.Equal(t, reason.Error(), tc.Error())
+		case <-time.After(500 * time.Millisecond):
+			t.Error("peer did not return")
 		}
-	case <-time.After(500 * time.Millisecond):
-		t.Error("peer did not return")
+		closer()
 	}
 }
 
```
