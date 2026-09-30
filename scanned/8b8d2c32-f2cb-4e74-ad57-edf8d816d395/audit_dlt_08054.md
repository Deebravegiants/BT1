# [?] swarm/pss: Reduce input vulnerabilities (#18304)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-12-18
Source: https://github.com/celo-org/celo-blockchain/commit/b01cfce36276379a95deb1001a6f1b6a048609de
Type: security-commit

## Details
swarm/pss: Reduce input vulnerabilities (#18304)

## Patch
### swarm/pss/api.go
```diff
@@ -92,7 +92,7 @@ func (pssapi *API) Receive(ctx context.Context, topic Topic, raw bool, prox bool
 }
 
 func (pssapi *API) GetAddress(topic Topic, asymmetric bool, key string) (PssAddress, error) {
-	var addr *PssAddress
+	var addr PssAddress
 	if asymmetric {
 		peer, ok := pssapi.Pss.pubKeyPool[key][topic]
 		if !ok {
@@ -107,7 +107,7 @@ func (pssapi *API) GetAddress(topic Topic, asymmetric bool, key string) (PssAddr
 		addr = peer.address
 
 	}
-	return *addr, nil
+	return addr, nil
 }
 
 // Retrieves the node's base address in hex form
@@ -128,7 +128,7 @@ func (pssapi *API) SetPeerPublicKey(pubkey hexutil.Bytes, topic Topic, addr PssA
 	if err != nil {
 		return fmt.Errorf("Cannot unmarshal pubkey: %x", pubkey)
 	}
-	err = pssapi.Pss.SetPeerPublicKey(pk, topic, &addr)
+	err = pssapi.Pss.SetPeerPublicKey(pk, topic, addr)
 	if err != nil {
 		return fmt.Errorf("Invalid key: %x", pk)
 	}
@@ -141,11 +141,11 @@ func (pssapi *API) GetSymmetricKey(symkeyid string) (hexutil.Bytes, error) {
 }
 
 func (pssapi *API) GetSymmetricAddressHint(topic Topic, symkeyid string) (PssAddress, error) {
-	return *pssapi.Pss.symKeyPool[symkeyid][topic].address, nil
+	return pssapi.Pss.symKeyPool[symkeyid][topic].address, nil
 }
 
 func (pssapi *API) GetAsymmetricAddressHint(topic Topic, pubkeyid string) (PssAddress, error) {
-	return *pssapi.Pss.pubKeyPool[pubkeyid][topic].address, nil
+	return pssapi.Pss.pubKeyPool[pubkeyid][topic].address, nil
 }
 
 func (pssapi *API) StringToTopic(topicstring string) (Topic, error) {
@@ -157,14 +157,23 @@ func (pssapi *API) StringToTopic(topicstring string) (Topic, error) {
 }
 
 func (pssapi *API) SendAsym(pubkeyhex string, topic Topic, msg hexutil.Bytes) error {
+	if err := validateMsg(msg); err != nil {
+		return err
+	}
 	return pssapi.Pss.SendAsym(pubkeyhex, topic, msg[:])
 }
 
 func (pssapi *API) SendSym(symkeyhex string, topic Topic, msg hexutil.Bytes) error {
+	if err := validateMsg(msg); err != nil {
+		return err
+	}
 	return pssapi.Pss.SendSym(symkeyhex, topic, msg[:])
 }
 
 func (pssapi *API) SendRaw(addr hexutil.Bytes, topic Topic, msg hexutil.Bytes) error {
+	if err := validateMsg(msg); err != nil {
+		return err
+	}
 	return pssapi.Pss.SendRaw(PssAddress(addr), topic, msg[:])
 }
 
@@ -177,3 +186,10 @@ func (pssapi *API) GetPeerTopics(pubkeyhex string) ([]Topic, error) {
 func (pssapi *API) GetPeerAddress(pubkeyhex string, topic Topic) (PssAddress, error) {
 	return pssapi.Pss.getPeerAddress(pubkeyhex, topic)
 }
+
+func validateMsg(msg []byte) error {
+	if len(msg) == 0 {
+		return errors.New("invalid message length")
+	}
+	return nil
+}
```

### swarm/pss/handshake.go
```diff
@@ -321,9 +321,7 @@ func (ctl *HandshakeController) handleKeys(pubkeyid string, keymsg *handshakeMsg
 		for _, key := range keymsg.Keys {
 			sendsymkey := make([]byte, len(key))
 			copy(sendsymkey, key)
-			var address PssAddress
-			copy(address[:], keymsg.From)
-			sendsymkeyid, err := ctl.pss.setSymmetricKey(sendsymkey, keymsg.Topic, &address, false, false)
+			sendsymkeyid, err := ctl.pss.setSymmetricKey(sendsymkey, keymsg.Topic, PssAddress(keymsg.From), false, false)
 			if err != nil {
 				return err
 			}
@@ -356,7 +354,7 @@ func (ctl *HandshakeController) handleKeys(pubkeyid string, keymsg *handshakeMsg
 func (ctl *HandshakeController) sendKey(pubkeyid string, topic *Topic, keycount uint8) ([]string, error) {
 
 	var requestcount uint8
-	to := &PssAddress{}
+	to := PssAddress{}
 	if _, ok := ctl.pss.pubKeyPool[pubkeyid]; !ok {
 		return []string{}, errors.New("Invalid public key")
 	} else if psp, ok := ctl.pss.pubKeyPool[pubkeyid][*topic]; ok {
@@ -564,5 +562,5 @@ func (api *HandshakeAPI) SendSym(symkeyid string, topic Topic, msg hexutil.Bytes
 		api.ctrl.symKeyIndex[symkeyid].count++
 		log.Trace("increment symkey send use", "symkeyid", symkeyid, "count", api.ctrl.symKeyIndex[symkeyid].count, "limit", api.ctrl.symKeyIndex[symkeyid].limit, "receiver", common.ToHex(crypto.FromECDSAPub(api.ctrl.pss.PublicKey())))
 	}
-	return
+	return err
 }
```

### swarm/pss/handshake_test.go
```diff
@@ -30,6 +30,7 @@ import (
 // asymmetrical key exchange between two directly connected peers
 // full address, partial address (8 bytes) and empty address
 func TestHandshake(t *testing.T) {
+	t.Skip("handshakes are not adapted to current pss core code")
 	t.Run("32", testHandshake)
 	t.Run("8", testHandshake)
 	t.Run("0", testHandshake)
```

### swarm/pss/notify/notify.go
```diff
@@ -138,7 +138,7 @@ func (c *Controller) Subscribe(name string, pubkey *ecdsa.PublicKey, address pss
 	c.mu.Lock()
 	defer c.mu.Unlock()
 	msg := NewMsg(MsgCodeStart, name, c.pss.BaseAddr())
-	c.pss.SetPeerPublicKey(pubkey, controlTopic, &address)
+	c.pss.SetPeerPublicKey(pubkey, controlTopic, address)
 	pubkeyId := hexutil.Encode(crypto.FromECDSAPub(pubkey))
 	smsg, err := rlp.EncodeToBytes(msg)
 	if err != nil {
@@ -271,7 +271,7 @@ func (c *Controller) addToBin(ntfr *notifier, address []byte) (symKeyId string,
 		currentBin.count++
 		symKeyId = currentBin.symKeyId
 	} else {
-		symKeyId, err = c.pss.GenerateSymmetricKey(ntfr.topic, &pssAddress, false)
+		symKeyId, err = c.pss.GenerateSymmetricKey(ntfr.topic, pssAddress, false)
 		if err != nil {
 			return "", nil, err
 		}
@@ -312,7 +312,7 @@ func (c *Controller) handleStartMsg(msg *Msg, keyid string) (err error) {
 	if err != nil {
 		return err
 	}
-	err = c.pss.SetPeerPublicKey(pubkey, controlTopic, &pssAddress)
+	err = c.pss.SetPeerPublicKey(pubkey, controlTopic, pssAddress)
 	if err != nil {
 		return err
 	}
@@ -335,7 +335,7 @@ func (c *Controller) handleNotifyWithKeyMsg(msg *Msg) error {
 
 	// \TODO keep track of and add actual address
 	updaterAddr := pss.PssAddress([]byte{})
-	c.pss.SetSymmetricKey(symkey, topic, &updaterAddr, true)
+	c.pss.SetSymmetricKey(symkey, topic, updaterAddr, true)
 	c.pss.Register(&topic, pss.NewHandler(c.Handler))
 	return c.subscriptions[msg.namestring].handler(msg.namestring, msg.Payload[:len(msg.Payload)-symKeyLength])
 }
```

### swarm/pss/pss.go
```diff
@@ -81,7 +81,7 @@ type senderPeer interface {
 // member `protected` prevents garbage collection of the instance
 type pssPeer struct {
 	lastSeen  time.Time
-	address   *PssAddress
+	address   PssAddress
 	protected bool
 }
 
@@ -396,9 +396,11 @@ func (p *Pss) handlePssMsg(ctx context.Context, msg interface{}) error {
 	// raw is simplest handler contingency to check, so check that first
 	var isRaw bool
 	if pssmsg.isRaw() {
-		if !p.topicHandlerCaps[psstopic].raw {
-			log.Debug("No handler for raw message", "topic", psstopic)
-			return nil
+		if _, ok := p.topicHandlerCaps[psstopic]; ok {
+			if !p.topicHandlerCaps[psstopic].raw {
+				log.Debug("No handler for raw message", "topic", psstopic)
+				return nil
+			}
 		}
 		isRaw = true
 	}
@@ -437,10 +439,10 @@ func (p *Pss) process(pssmsg *PssMsg, raw bool, prox bool) error {
 	var err error
 	var recvmsg *whisper.ReceivedMessage
 	var payload []byte
-	var from *PssAddress
+	var from PssAddress
 	var asymmetric bool
 	var keyid string
-	var keyFunc func(envelope *whisper.Envelope) (*whisper.ReceivedMessage, string, *PssAddress, error)
+	var keyFunc func(envelope *whisper.Envelope) (*whisper.ReceivedMessage, string, PssAddress, error)
 
 	envelope := pssmsg.Payload
 	psstopic := Topic(envelope.Topic)
@@ -473,7 +475,7 @@ func (p *Pss) process(pssmsg *PssMsg, raw bool, prox bool) error {
 
 }
 
-func (p *Pss) executeHandlers(topic Topic, payload []byte, from *PssAddress, raw bool, prox bool, asymmetric bool, keyid string) {
+func (p *Pss) executeHandlers(topic Topic, payload []byte, from PssAddress, raw bool, prox bool, asymmetric bool, keyid string) {
 	handlers := p.getHandlers(topic)
 	peer := p2p.NewPeer(enode.ID{}, fmt.Sprintf("%x", from), []p2p.Cap{})
 	for h := range handlers {
@@ -528,7 +530,10 @@ func (p *Pss) isSelfPossibleRecipient(msg *PssMsg, prox bool) bool {
 //
 // The value in `address` will be used as a routing hint for the
 // public key / topic association
-func (p *Pss) SetPeerPublicKey(pubkey *ecdsa.PublicKey, topic Topic, address *PssAddress) error {
+func (p *Pss) SetPeerPublicKey(pubkey *ecdsa.PublicKey, topic Topic, address PssAddress) error {
+	if err := validateAddress(address); err != nil {
+		return err
+	}
 	pubkeybytes := crypto.FromECDSAPub(pubkey)
 	if len(pubkeybytes) == 0 {
 		return fmt.Errorf("invalid public key: %v", pubkey)
@@ -543,12 +548,12 @@ func (p *Pss) SetPeerPublicKey(pubkey *ecdsa.PublicKey, topic Topic, address *Ps
 	}
 	p.pubKeyPool[pubkeyid][topic] = psp
 	p.pubKeyPoolMu.Unlock()
-	log.Trace("added pubkey", "pubkeyid", pubkeyid, "topic", topic, "address", common.ToHex(*address))
+	log.Trace("added pubkey", "pubkeyid", pubkeyid, "topic", topic, "address", address)
 	return nil
 }
 
 // Automatically generate a new symkey for a topic and address hint
-func (p *Pss) GenerateSymmetricKey(topic Topic, address *PssAddress, addToCache bool) (string, error) {
+func (p *Pss) GenerateSymmetricKey(topic Topic, address PssAddress, addToCache bool) (string, error) {
 	keyid, err := p.w.GenerateSymKey()
 	if err != nil {
 		return "", err
@@ -569,11 +574,14 @@ func (p *Pss) GenerateSymmetricKey(topic Topic, address *PssAddress, addToCache
 //
 // Returns a string id that can be used to retrieve the key bytes
 // from the whisper backend (see pss.GetSymmetricKey())
-func (p *Pss) SetSymmetricKey(key []byte, topic Topic, address *PssAddress, addtocache bool) (string, error) {
+func (p *Pss) SetSymmetricKey(key []byte, topic Topic, address PssAddress, addtocache bool) (string, error) {
+	if err := validateAddress(address); err != nil {
+		return "", err
+	}
 	return p.setSymmetricKey(key, topic, address, addtocache, true)
 }
 
-func (p *Pss) setSymmetricKey(key []byte, topic Topic, address *PssAddress, addtocache bool, protected bool) (string, error) {
+func (p *Pss) setSymmetricKey(key []byte, topic Topic, address PssAddress, addtocache bool, protected bool) (string, error) {
 	keyid, err := p.w.AddSymKeyDirect(key)
 	if err != nil {
 		return "", err
@@ -585,7 +593,7 @@ func (p *Pss) setSymmetricKey(key []byte, topic Topic, address *PssAddress, addt
 // adds a symmetric key to the pss key pool, and optionally adds the key
 // to the collection of keys used to attempt symmetric decryption of
 // incoming messages
-func (p *Pss) addSymmetricKeyToPool(keyid string, topic Topic, address *PssAddress, addtocache bool, protected bool) {
+func (p *Pss) addSymmetricKeyToPool(keyid string, topic Topic, address PssAddress, addtocache bool, protected bool) {
 	psp := &pssPeer{
 		address:   address,
 		protected: protected,
@@ -601,7 +609,7 @@ func (p *Pss) addSymmetricKeyToPool(keyid string, topic Topic, address *PssAddre
 		p.symKeyDecryptCache[p.symKeyDecryptCacheCursor%cap(p.symKeyDecryptCache)] = &keyid
 	}
 	key, _ := p.GetSymmetricKey(keyid)
-	log.Trace("added symkey", "symkeyid", keyid, "symkey", common.ToHex(key), "topic", topic, "address", fmt.Sprintf("%p", address), "cache", addtocache)
+	log.Trace("added symkey", "symkeyid", keyid, "symkey", common.ToHex(key), "topic", topic, "address", address, "cache", addtocache)
 }
 
 // Returns a symmetric key byte seqyence stored in the whisper backend
@@ -622,7 +630,7 @@ func (p *Pss) GetPublickeyPeers(keyid string) (topic []Topic, address []PssAddre
 	defer p.pubKeyPoolMu.RUnlock()
 	for t, peer := range p.pubKeyPool[keyid] {
 		topic = append(topic, t)
-		address = append(address, *peer.address)
+		address = append(address, peer.address)
 	}
 
 	return topic, address, nil
@@ -633,7 +641,7 @@ func (p *Pss) getPeerAddress(keyid string, topic Topic) (PssAddress, error) {
 	defer p.pubKeyPoolMu.RUnlock()
 	if peers, ok := p.pubKeyPool[keyid]; ok {
 		if t, ok := peers[topic]; ok {
-			return *t.address, nil
+			return t.address, nil
 		}
 	}
 	return nil, fmt.Errorf("peer with pubkey %s, topic %x not found", keyid, topic)
@@ -645,7 +653,7 @@ func (p *Pss) getPeerAddress(keyid string, topic Topic) (PssAddress, error) {
 // encapsulating the decrypted message, and the whisper backend id
 // of the symmetric key used to decrypt the message.
 // It fails if decryption of the message fails or if the message is corrupted
-func (p *Pss) processSym(envelope *whisper.Envelope) (*whisper.ReceivedMessage, string, *PssAddress, error) {
+func (p *Pss) processSym(envelope *whisper.Envelope) (*whisper.ReceivedMessage, string, PssAddress, error) {
 	metrics.GetOrRegisterCounter("pss.process.sym", nil).Inc(1)
 
 	for i := p.symKeyDecryptCacheCursor; i > p.symKeyDecryptCacheCursor-cap(p.symKeyDecryptCache) && i > 0; i-- {
@@ -677,7 +685,7 @@ func (p *Pss) processSym(envelope *whisper.Envelope) (*whisper.ReceivedMessage,
 // encapsulating the decrypted message, and the byte representation of
 // the public key used to decrypt the message.
 // It fails if decryption of message fails, or if the message is corrupted
-func (p *Pss) processAsym(envelope *whisper.Envelope) (*whisper.ReceivedMessage, string, *PssAddress, error) {
+func (p *Pss) processAsym(envelope *whisper.Envelope) (*whisper.ReceivedMessage, string, PssAddress, error) {
 	metrics.GetOrRegisterCounter("pss.process.asym", nil).Inc(1)
 
 	recvmsg, err := envelope.OpenAsymmetric(p.privateKey)
@@ -689,7 +697,7 @@ func (p *Pss) processAsym(envelope *whisper.Envelope) (*whisper.ReceivedMessage,
 		return nil, "", nil, fmt.Errorf("invalid message")
 	}
 	pubkeyid := common.ToHex(crypto.FromECDSAPub(recvmsg.Src))
-	var from *PssAddress
+	var from PssAddress
 	p.pubKeyPoolMu.Lock()
 	if p.pubKeyPool[pubkeyid][Topic(envelope.Topic)] != nil {
 		from = p.pubKeyPool[pubkeyid][Topic(envelope.Topic)].address
@@ -751,6 +759,9 @@ func (p *Pss) enqueue(msg *PssMsg) error {
 //
 // Will fail if raw messages are disallowed
 func (p *Pss) SendRaw(address PssAddress, topic Topic, msg []byte) error {
+	if err := validateAddress(address); err != nil {
+		return err
+	}
 	pssMsgParams := &msgParams{
 		raw: true,
 	}
@@ -770,8 +781,10 @@ func (p *Pss) SendRaw(address PssAddress, topic Topic, msg []byte) error {
 
 	// if we have a proxhandler on this topic
 	// also deliver message to ourselves
-	if p.isSelfPossibleRecipient(pssMsg, true) && p.topicHandlerCaps[topic].prox {
-		return p.process(pssMsg, true, true)
+	if _, ok := p.topicHandlerCaps[topic]; ok {
+		if p.isSelfPossibleRecipient(pssMsg, true) && p.topicHandlerCaps[topic].prox {
+			return p.process(pssMsg, true, true)
+		}
 	}
 	return nil
 }
@@ -789,11 +802,8 @@ func (p *Pss) SendSym(symkeyid string, topic Topic, msg []byte) error {
 	p.symKeyPoolMu.Unlock()
 	if !ok {
 		return fmt.Errorf("invalid topic '%s' for symkey '%s'", topic.String(), symkeyid)
-	} else if psp.address == nil {
-		return fmt.Errorf("no address hint for topic '%s' symkey '%s'", topic.String(), symkeyid)
 	}
-	err = p.send(*psp.address, topic, msg, false, symkey)
-	return err
+	return p.send(psp.address, topic, msg, false, symkey)
 }
 
 // Send a message using asymmetric encryption
@@ -808,13 +818,8 @@ func (p *Pss) SendAsym(pubkeyid string, topic Topic, msg []byte) error {
 	p.pubKeyPoolMu.Unlock()
 	if !ok {
 		return fmt.Errorf("invalid topic '%s' for pubkey '%s'", topic.String(), pubkeyid)
-	} else if psp.address == nil {
-		return fmt.Errorf("no address hint for topic '%s' pubkey '%s'", topic.String(), pubkeyid)
 	}
-	go func() {
-		p.send(*psp.address, topic, msg, true, common.FromHex(pubkeyid))
-	}()
-	return nil
+	return p.send(psp.address, topic, msg, true, common.FromHex(pubkeyid))
 }
 
 // Send is payload agnostic, and will accept any byte slice as payload
@@ -1034,3 +1039,10 @@ func (p *Pss) digestBytes(msg []byte) pssDigest {
 	copy(digest[:], key[:digestLength])
 	return digest
 }
+
+func validateAddress(addr PssAddress) error {
+	if len(addr) > addressLength {
+		return errors.New("address too long")
+	}
+	return nil
+}
```

### swarm/pss/pss_test.go
```diff
@@ -407,7 +407,7 @@ func TestProxShortCircuit(t *testing.T) {
 
 	// try the same prox message with sym and asym send
 	proxAddrPss := PssAddress(proxMessageAddress)
-	symKeyId, err := ps.GenerateSymmetricKey(topic, &proxAddrPss, true)
+	symKeyId, err := ps.GenerateSymmetricKey(topic, proxAddrPss, true)
 	go func() {
 		err := ps.SendSym(symKeyId, topic, []byte("baz"))
 		if err != nil {
@@ -424,7 +424,7 @@ func TestProxShortCircuit(t *testing.T) {
 		t.Fatal("sym timeout")
 	}
 
-	err = ps.SetPeerPublicKey(&privKey.PublicKey, topic, &proxAddrPss)
+	err = ps.SetPeerPublicKey(&privKey.PublicKey, topic, proxAddrPss)
 	if err != nil {
 		t.Fatal(err)
 	}
@@ -786,14 +786,14 @@ func TestKeys(t *testing.T) {
 	copy(addr, network.RandomAddr().Over())
 	outkey := network.RandomAddr().Over()
 	topicobj := BytesToTopic([]byte("foo:42"))
-	ps.SetPeerPublicKey(&theirprivkey.PublicKey, topicobj, &addr)
-	outkeyid, err := ps.SetSymmetricKey(outkey, topicobj, &addr, false)
+	ps.SetPeerPublicKey(&theirprivkey.PublicKey, topicobj, addr)
+	outkeyid, err := ps.SetSymmetricKey(outkey, topicobj, addr, false)
 	if err != nil {
 		t.Fatalf("failed to set 'our' outgoing symmetric key")
 	}
 
 	// make a symmetric key that we will send to peer for encrypting messages to us
-	inkeyid, err := ps.GenerateSymmetricKey(topicobj, &addr, true)
+	inkeyid, err := ps.GenerateSymmetricKey(topicobj, addr, true)
 	if err != nil {
 		t.Fatalf("failed to set 'our' incoming symmetric key")
 	}
@@ -816,8 +816,8 @@ func TestKeys(t *testing.T) {
 
 	// check that the key is stored in the peerpool
 	psp := ps.symKeyPool[inkeyid][topicobj]
-	if psp.address != &addr {
-		t.Fatalf("inkey address does not match; %p != %p", psp.address, &addr)
+	if !bytes.Equal(psp.address, addr) {
+		t.Fatalf("inkey address does not match; %p != %p", psp.address, addr)
 	}
 }
 
@@ -1008,6 +1008,34 @@ func TestRawAllow(t *testing.T) {
 	}
 }
 
+// BELOW HERE ARE TESTS USING THE SIMULATION FRAMEWORK
+
+// tests that the API layer can handle edge case values
+func TestApi(t *testing.T) {
+	clients, err := setupNetwork(2, true)
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	topic := "0xdeadbeef"
+
+	err = clients[0].Call(nil, "pss_sendRaw", "0x", topic, "0x666f6f")
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	err = clients[0].Call(nil, "pss_sendRaw", "0xabcdef", topic, "0x")
+	if err == nil {
+		t.Fatal("expected error on empty msg")
+	}
+
+	overflowAddr := [33]byte{}
+	err = clients[0].Call(nil, "pss_sendRaw", hexutil.Encode(overflowAddr[:]), topic, "0x666f6f")
+	if err == nil {
+		t.Fatal("expected error on send too big address")
+	}
+}
+
 // verifies that nodes can send and receive raw (verbatim) messages
 func TestSendRaw(t *testing.T) {
 	t.Run("32", testSendRaw)
@@ -1668,15 +1696,15 @@ func benchmarkSymKeySend(b *testing.B) {
 	topic := BytesToTopic([]byte("foo"))
 	to := make(PssAddress, 32)
 	copy(to[:], network.RandomAddr().Over())
-	symkeyid, err := ps.GenerateSymmetricKey(topic, &to, true)
+	symkeyid, err := ps.GenerateSymmetricKey(topic, to, true)
 	if err != nil {
 		b.Fatalf("could not generate symkey: %v", err)
 	}
 	symkey, err := ps.w.GetSymKey(symkeyid)
 	if err != nil {
 		b.Fatalf("could not retrieve symkey: %v", err)
 	}
-	ps.SetSymmetricKey(symkey, topic, &to, false)
+	ps.SetSymmetricKey(symkey, topic, to, false)
 
 	b.ResetTimer()
 	for i := 0; i < b.N; i++ {
@@ -1712,7 +1740,7 @@ func benchmarkAsymKeySend(b *testing.B) {
 	topic := BytesToTopic([]byte("foo"))
 	to := make(PssAddress, 32)
 	copy(to[:], network.RandomAddr().Over())
-	ps.SetPeerPublicKey(&privkey.PublicKey, topic, &to)
+	ps.SetPeerPublicKey(&privkey.PublicKey, topic, to)
 	b.ResetTimer()
 	for i := 0; i < b.N; i++ {
 		ps.SendAsym(common.ToHex(crypto.FromECDSAPub(&privkey.PublicKey)), topic, msg)
@@ -1761,7 +1789,7 @@ func benchmarkSymkeyBruteforceChangeaddr(b *testing.B) {
 	for i := 0; i < int(keycount); i++ {
 		to := make(PssAddress, 32)
 		copy(to[:], network.RandomAddr().Over())
-		keyid, err = ps.GenerateSymmetricKey(topic, &to, true)
+		keyid, err = ps.GenerateSymmetricKey(topic, to, true)
 		if err != nil {
 			b.Fatalf("cant generate symkey #%d: %v", i, err)
 		}
@@ -1843,7 +1871,7 @@ func benchmarkSymkeyBruteforceSameaddr(b *testing.B) {
 	topic := BytesToTopic([]byte("foo"))
 	for i := 0; i < int(keycount); i++ {
 		copy(addr[i], network.RandomAddr().Over())
-		keyid, err = ps.GenerateSymmetricKey(topic, &addr[i], true)
+		keyid, err = ps.GenerateSymmetricKey(topic, addr[i], true)
 		if err != nil {
 			b.Fatalf("cant generate symkey #%d: %v", i, err)
 		}
@@ -2044,12 +2072,13 @@ func NewAPITest(ps *Pss) *APITest {
 	return &APITest{Pss: ps}
 }
 
-func (apitest *APITest) SetSymKeys(pubkeyid string, recvsymkey []byte, sendsymkey []byte, limit uint16, topic Topic, to PssAddress) ([2]string, error) {
-	recvsymkeyid, err := apitest.SetSymmetricKey(recvsymkey, topic, &to, true)
+func (apitest *APITest) SetSymKeys(pubkeyid string, recvsymkey []byte, sendsymkey []byte, limit uint16, topic Topic, to hexutil.Bytes) ([2]string, error) {
+
+	recvsymkeyid, err := apitest.SetSymmetricKey(recvsymkey, topic, PssAddress(to), true)
 	if err != nil {
 		return [2]string{}, err
 	}
-	sendsymkeyid, err := apitest.SetSymmetricKey(sendsymkey, topic, &to, false)
+	sendsymkeyid, err := apitest.SetSymmetricKey(sendsymkey, topic, PssAddress(to), false)
 	if err != nil {
 		return [2]string{}, err
 	}
```
