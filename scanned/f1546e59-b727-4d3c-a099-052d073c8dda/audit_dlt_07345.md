# [?] Fix data race at discovery (#859)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-03-15
Source: https://github.com/hyperledger/fabric/commit/af7980f51fef5d4bcc519746fae10194113fb900
Type: security-commit

## Details
Fix data race at discovery (#859)

When dead members are being expired, the expired members
are copied by reference into a slice under a lock.

These members can be changed under a lock, however
they are sometimes logged without the lock.

Implemented a Clone() method and used it when the network members
are logged.

Change-Id: Ic40a802ce5ea47dd11c3d38ccaf125ce64d97402
Signed-off-by: yacovm <yacovm@il.ibm.com>

## Patch
### gossip/discovery/discovery.go
```diff
@@ -9,6 +9,7 @@ package discovery
 import (
 	"fmt"
 
+	protolib "github.com/golang/protobuf/proto"
 	proto "github.com/hyperledger/fabric-protos-go/gossip"
 	"github.com/hyperledger/fabric/gossip/common"
 	"github.com/hyperledger/fabric/gossip/protoext"
@@ -82,6 +83,28 @@ type NetworkMember struct {
 	*proto.Envelope
 }
 
+// Clone clones the NetworkMember
+func (n NetworkMember) Clone() NetworkMember {
+	pkiIDClone := make(common.PKIidType, len(n.PKIid))
+	copy(pkiIDClone, n.PKIid)
+	nmClone := NetworkMember{
+		Endpoint:         n.Endpoint,
+		Metadata:         n.Metadata,
+		InternalEndpoint: n.InternalEndpoint,
+		PKIid:            pkiIDClone,
+	}
+
+	if n.Properties != nil {
+		nmClone.Properties = protolib.Clone(n.Properties).(*proto.Properties)
+	}
+
+	if n.Envelope != nil {
+		nmClone.Envelope = protolib.Clone(n.Envelope).(*proto.Envelope)
+	}
+
+	return nmClone
+}
+
 // String returns a string representation of the NetworkMember
 func (n NetworkMember) String() string {
 	return fmt.Sprintf("Endpoint: %s, InternalEndpoint: %s, PKI-ID: %s, Metadata: %x", n.Endpoint, n.InternalEndpoint, n.PKIid, n.Metadata)
```

### gossip/discovery/discovery_impl.go
```diff
@@ -703,15 +703,15 @@ func (d *gossipDiscoveryImpl) expireDeadMembers(dead []common.PKIidType) {
 	d.logger.Warning("Entering", dead)
 	defer d.logger.Warning("Exiting")
 
-	var deadMembers2Expire []*NetworkMember
+	var deadMembers2Expire []NetworkMember
 
 	d.lock.Lock()
 
 	for _, pkiID := range dead {
 		if _, isAlive := d.aliveLastTS[string(pkiID)]; !isAlive {
 			continue
 		}
-		deadMembers2Expire = append(deadMembers2Expire, d.id2Member[string(pkiID)])
+		deadMembers2Expire = append(deadMembers2Expire, d.id2Member[string(pkiID)].Clone())
 		// move lastTS from alive to dead
 		lastTS, hasLastTS := d.aliveLastTS[string(pkiID)]
 		if hasLastTS {
@@ -729,7 +729,7 @@ func (d *gossipDiscoveryImpl) expireDeadMembers(dead []common.PKIidType) {
 
 	for _, member2Expire := range deadMembers2Expire {
 		d.logger.Warning("Closing connection to", member2Expire)
-		d.comm.CloseConn(member2Expire)
+		d.comm.CloseConn(&member2Expire)
 	}
 }
 
```

### gossip/discovery/discovery_test.go
```diff
@@ -428,6 +428,27 @@ func bootPeer(port int) string {
 	return fmt.Sprintf("localhost:%d", port)
 }
 
+func TestClone(t *testing.T) {
+	nm := &NetworkMember{
+		PKIid: common.PKIidType("abc"),
+		Properties: &proto.Properties{
+			LedgerHeight: 1,
+			LeftChannel:  true,
+		},
+		Envelope: &proto.Envelope{
+			Payload: []byte("payload"),
+		},
+		InternalEndpoint: "internal",
+		Metadata:         []byte{1, 2, 3},
+		Endpoint:         "endpoint",
+	}
+
+	nm2 := nm.Clone()
+	assert.Equal(t, *nm, nm2, "Clones are different")
+	assert.False(t, nm.Properties == nm2.Properties, "Cloning should be deep and not shallow")
+	assert.False(t, nm.Envelope == nm2.Envelope, "Cloning should be deep and not shallow")
+}
+
 func TestHasExternalEndpoints(t *testing.T) {
 	memberWithEndpoint := NetworkMember{Endpoint: "foo"}
 	memberWithoutEndpoint := NetworkMember{}
```
