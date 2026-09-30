# [?] swarm/pss: fix data race on HandshakeController.symKeyIndex (#19162)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-02-26
Source: https://github.com/celo-org/celo-blockchain/commit/340a53a98bd760fab229ea9daa70adddf7460a78
Type: security-commit

## Details
swarm/pss: fix data race on HandshakeController.symKeyIndex (#19162)

* swarm/pss: fix data race on HandshakeController.symKeyIndex

The HandshakeController.symKeyIndex map was accessed concurrently.
Since insufficient test coverage the race is not detected every time.
However, running TestClientHandshake a 100 times seems to be enough to
reproduce the race.

Note: I've chosen HandshakeController.lock to protect
HandshakeController.symKeyIndex as that was already protected in a few
functions by that lock.

Additionally:
- removed unused testStore
- enabled tests in handshake_test.go as they pass
- removed code duplication by adding getSymKey()

* swarm/pss: fix a data race on HandshakeController.keyC

* swarm/pss: fix data races with on Pss.symKeyPool

## Patch
### swarm/pss/client/client_test.go
```diff
@@ -23,7 +23,6 @@ import (
 	"fmt"
 	"math/rand"
 	"os"
-	"sync"
 	"testing"
 	"time"
 
@@ -286,18 +285,3 @@ func newServices() adapters.Services {
 		},
 	}
 }
-
-// copied from swarm/network/protocol_test_go
-type testStore struct {
-	sync.Mutex
-
-	values map[string][]byte
-}
-
-func (t *testStore) Load(key string) ([]byte, error) {
-	return nil, nil
-}
-
-func (t *testStore) Save(key string, v []byte) error {
-	return nil
-}
```

### swarm/pss/handshake.go
```diff
@@ -106,6 +106,7 @@ func NewHandshakeParams() *HandshakeParams {
 type HandshakeController struct {
 	pss                  *Pss
 	keyC                 map[string]chan []string // adds a channel to report when a handshake succeeds
+	keyCMu               sync.Mutex               // protects keyC map
 	lock                 sync.Mutex
 	symKeyRequestTimeout time.Duration
 	symKeyExpiryTimeout  time.Duration
@@ -165,9 +166,9 @@ func (ctl *HandshakeController) validKeys(pubkeyid string, topic *Topic, in bool
 
 	for _, key := range *keystore {
 		if key.limit <= key.count {
-			ctl.releaseKey(*key.symKeyID, topic)
+			ctl.releaseKeyNoLock(*key.symKeyID, topic)
 		} else if !key.expiredAt.IsZero() && key.expiredAt.Before(now) {
-			ctl.releaseKey(*key.symKeyID, topic)
+			ctl.releaseKeyNoLock(*key.symKeyID, topic)
 		} else {
 			validkeys = append(validkeys, key.symKeyID)
 		}
@@ -205,15 +206,23 @@ func (ctl *HandshakeController) updateKeys(pubkeyid string, topic *Topic, in boo
 			limit:    limit,
 		}
 		*keystore = append(*keystore, storekey)
+		ctl.pss.mx.Lock()
 		ctl.pss.symKeyPool[*storekey.symKeyID][*topic].protected = true
+		ctl.pss.mx.Unlock()
 	}
 	for i := 0; i < len(*keystore); i++ {
 		ctl.symKeyIndex[*(*keystore)[i].symKeyID] = &((*keystore)[i])
 	}
 }
 
-// Expire a symmetric key, making it elegible for garbage collection
 func (ctl *HandshakeController) releaseKey(symkeyid string, topic *Topic) bool {
+	ctl.lock.Lock()
+	defer ctl.lock.Unlock()
+	return ctl.releaseKeyNoLock(symkeyid, topic)
+}
+
+// Expire a symmetric key, making it eligible for garbage collection
+func (ctl *HandshakeController) releaseKeyNoLock(symkeyid string, topic *Topic) bool {
 	if ctl.symKeyIndex[symkeyid] == nil {
 		log.Debug("no symkey", "symkeyid", symkeyid)
 		return false
@@ -276,30 +285,49 @@ func (ctl *HandshakeController) clean() {
 	}
 }
 
+func (ctl *HandshakeController) getSymKey(symkeyid string) *handshakeKey {
+	ctl.lock.Lock()
+	defer ctl.lock.Unlock()
+	return ctl.symKeyIndex[symkeyid]
+}
+
 // Passed as a PssMsg handler for the topic handshake is activated on
 // Handles incoming key exchange messages and
-// ccunts message usage by symmetric key (expiry limit control)
+// counts message usage by symmetric key (expiry limit control)
 // Only returns error if key handler fails
 func (ctl *HandshakeController) handler(msg []byte, p *p2p.Peer, asymmetric bool, symkeyid string) error {
-	if !asymmetric {
-		if ctl.symKeyIndex[symkeyid] != nil {
-			if ctl.symKeyIndex[symkeyid].count >= ctl.symKeyIndex[symkeyid].limit {
-				return fmt.Errorf("discarding message using expired key: %s", symkeyid)
+	if asymmetric {
+		keymsg := &handshakeMsg{}
+		err := rlp.DecodeBytes(msg, keymsg)
+		if err == nil {
+			err := ctl.handleKeys(symkeyid, keymsg)
+			if err != nil {
+				log.Error("handlekeys fail", "error", err)
 			}
-			ctl.symKeyIndex[symkeyid].count++
-			log.Trace("increment symkey recv use", "symsymkeyid", symkeyid, "count", ctl.symKeyIndex[symkeyid].count, "limit", ctl.symKeyIndex[symkeyid].limit, "receiver", common.ToHex(crypto.FromECDSAPub(ctl.pss.PublicKey())))
+			return err
 		}
 		return nil
 	}
-	keymsg := &handshakeMsg{}
-	err := rlp.DecodeBytes(msg, keymsg)
-	if err == nil {
-		err := ctl.handleKeys(symkeyid, keymsg)
-		if err != nil {
-			log.Error("handlekeys fail", "error", err)
-		}
-		return err
+	return ctl.registerSymKeyUse(symkeyid)
+}
+
+func (ctl *HandshakeController) registerSymKeyUse(symkeyid string) error {
+	ctl.lock.Lock()
+	defer ctl.lock.Unlock()
+
+	symKey, ok := ctl.symKeyIndex[symkeyid]
+	if !ok {
+		return nil
 	}
+
+	if symKey.count >= symKey.limit {
+		return fmt.Errorf("symetric key expired (id: %s)", symkeyid)
+	}
+	symKey.count++
+
+	receiver := common.ToHex(crypto.FromECDSAPub(ctl.pss.PublicKey()))
+	log.Trace("increment symkey recv use", "symsymkeyid", symkeyid, "count", symKey.count, "limit", symKey.limit, "receiver", receiver)
+
 	return nil
 }
 
@@ -417,6 +445,8 @@ func (ctl *HandshakeController) sendKey(pubkeyid string, topic *Topic, keycount
 
 // Enables callback for keys received from a key exchange request
 func (ctl *HandshakeController) alertHandshake(pubkeyid string, symkeys []string) chan []string {
+	ctl.keyCMu.Lock()
+	defer ctl.keyCMu.Unlock()
 	if len(symkeys) > 0 {
 		if _, ok := ctl.keyC[pubkeyid]; ok {
 			ctl.keyC[pubkeyid] <- symkeys
@@ -519,7 +549,7 @@ func (api *HandshakeAPI) GetHandshakeKeys(pubkeyid string, topic Topic, in bool,
 // Returns the amount of messages the specified symmetric key
 // is still valid for under the handshake scheme
 func (api *HandshakeAPI) GetHandshakeKeyCapacity(symkeyid string) (uint16, error) {
-	storekey := api.ctrl.symKeyIndex[symkeyid]
+	storekey := api.ctrl.getSymKey(symkeyid)
 	if storekey == nil {
 		return 0, fmt.Errorf("invalid symkey id %s", symkeyid)
 	}
@@ -529,7 +559,7 @@ func (api *HandshakeAPI) GetHandshakeKeyCapacity(symkeyid string) (uint16, error
 // Returns the byte representation of the public key in ascii hex
 // associated with the given symmetric key
 func (api *HandshakeAPI) GetHandshakePublicKey(symkeyid string) (string, error) {
-	storekey := api.ctrl.symKeyIndex[symkeyid]
+	storekey := api.ctrl.getSymKey(symkeyid)
 	if storekey == nil {
 		return "", fmt.Errorf("invalid symkey id %s", symkeyid)
 	}
@@ -555,12 +585,8 @@ func (api *HandshakeAPI) ReleaseHandshakeKey(pubkeyid string, topic Topic, symke
 // for message expiry control
 func (api *HandshakeAPI) SendSym(symkeyid string, topic Topic, msg hexutil.Bytes) (err error) {
 	err = api.ctrl.pss.SendSym(symkeyid, topic, msg[:])
-	if api.ctrl.symKeyIndex[symkeyid] != nil {
-		if api.ctrl.symKeyIndex[symkeyid].count >= api.ctrl.symKeyIndex[symkeyid].limit {
-			return errors.New("attempted send with expired key")
-		}
-		api.ctrl.symKeyIndex[symkeyid].count++
-		log.Trace("increment symkey send use", "symkeyid", symkeyid, "count", api.ctrl.symKeyIndex[symkeyid].count, "limit", api.ctrl.symKeyIndex[symkeyid].limit, "receiver", common.ToHex(crypto.FromECDSAPub(api.ctrl.pss.PublicKey())))
+	if otherErr := api.ctrl.registerSymKeyUse(symkeyid); otherErr != nil {
+		return otherErr
 	}
 	return err
 }
```

### swarm/pss/handshake_test.go
```diff
@@ -14,8 +14,6 @@
 // You should have received a copy of the GNU Lesser General Public License
 // along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.
 
-// +build foo
-
 package pss
 
 import (
@@ -30,7 +28,6 @@ import (
 // asymmetrical key exchange between two directly connected peers
 // full address, partial address (8 bytes) and empty address
 func TestHandshake(t *testing.T) {
-	t.Skip("handshakes are not adapted to current pss core code")
 	t.Run("32", testHandshake)
 	t.Run("8", testHandshake)
 	t.Run("0", testHandshake)
@@ -47,7 +44,7 @@ func testHandshake(t *testing.T) {
 
 	// set up two nodes directly connected
 	// (we are not testing pss routing here)
-	clients, err := setupNetwork(2)
+	clients, err := setupNetwork(2, true)
 	if err != nil {
 		t.Fatal(err)
 	}
```

### swarm/pss/keystore.go
```diff
@@ -210,6 +210,8 @@ func (ks *Pss) processAsym(envelope *whisper.Envelope) (*whisper.ReceivedMessage
 // - it is not marked as protected
 // - it is not in the incoming decryption cache
 func (ks *Pss) cleanKeys() (count int) {
+	ks.mx.Lock()
+	defer ks.mx.Unlock()
 	for keyid, peertopics := range ks.symKeyPool {
 		var expiredtopics []Topic
 		for topic, psp := range peertopics {
@@ -229,10 +231,8 @@ func (ks *Pss) cleanKeys() (count int) {
 			}
 		}
 		for _, topic := range expiredtopics {
-			ks.mx.Lock()
 			delete(ks.symKeyPool[keyid], topic)
 			log.Trace("symkey cleanup deletion", "symkeyid", keyid, "topic", topic, "val", ks.symKeyPool[keyid])
-			ks.mx.Unlock()
 			count++
 		}
 	}
```
