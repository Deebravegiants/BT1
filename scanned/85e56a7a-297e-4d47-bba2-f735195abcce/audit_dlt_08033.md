# [?] Fix non-fatal panic on forwarding transactions without gateway fee (#667)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-11-28
Source: https://github.com/celo-org/celo-blockchain/commit/08401c6bbf8431e01d233fe01f90d80debd2e4cc
Type: security-commit

## Details
Fix non-fatal panic on forwarding transactions without gateway fee (#667)

## Patch
### les/peer.go
```diff
@@ -607,17 +607,20 @@ func (ps *peerSet) randomPeerEtherbase() common.Address {
 	return r
 }
 
-func (ps *peerSet) getPeerWithEtherbase(etherbase common.Address) (*peer, error) {
+func (ps *peerSet) getPeerWithEtherbase(etherbase *common.Address) (*peer, error) {
 	ps.lock.RLock()
 	defer ps.lock.RUnlock()
+	if etherbase == nil {
+		etherbase = new(common.Address)
+	}
 	var pid string
 	for id, petherbase := range ps.etherbases {
-		if etherbase == petherbase {
+		if *etherbase == petherbase {
 			pid = id
 		}
 	}
 	if pid == "" {
-		log.Info(errNoPeerWithEtherbaseFound.Error(), "etherbase", etherbase)
+		log.Info(errNoPeerWithEtherbaseFound.Error(), "etherbase", *etherbase)
 		return nil, errNoPeerWithEtherbaseFound
 	}
 	peer := ps.peers[pid]
```

### les/txrelay.go
```diff
@@ -64,7 +64,7 @@ func (self *LesTxRelay) unregisterPeer(p *peer) {
 	self.peerList = self.ps.AllPeers()
 }
 
-func (self *LesTxRelay) HasPeerWithEtherbase(etherbase common.Address) error {
+func (self *LesTxRelay) HasPeerWithEtherbase(etherbase *common.Address) error {
 	_, err := self.ps.getPeerWithEtherbase(etherbase)
 	return err
 }
@@ -78,7 +78,7 @@ func (self *LesTxRelay) send(txs types.Transactions) {
 		hash := tx.Hash()
 		ltr, ok := self.txSent[hash]
 		if !ok {
-			p, err := self.ps.getPeerWithEtherbase(*tx.GatewayFeeRecipient())
+			p, err := self.ps.getPeerWithEtherbase(tx.GatewayFeeRecipient())
 			// TODO(asa): When this happens, the nonce is still incremented, preventing future txs from being added.
 			// We rely on transactions to be rejected in light/txpool validateTx to prevent transactions
 			// with GatewayFeeRecipient != one of our peers from making it to the relayer.
```

### light/txpool.go
```diff
@@ -87,7 +87,7 @@ type TxRelayBackend interface {
 	Send(txs types.Transactions)
 	NewHead(head common.Hash, mined []common.Hash, rollback []common.Hash)
 	Discard(hashes []common.Hash)
-	HasPeerWithEtherbase(etherbase common.Address) error
+	HasPeerWithEtherbase(etherbase *common.Address) error
 }
 
 // NewTxPool creates a new light transaction pool
@@ -392,12 +392,7 @@ func (pool *TxPool) validateTx(ctx context.Context, tx *types.Transaction) error
 	}
 
 	// Should have a peer that will accept and broadcast our transaction
-	if tx.GatewayFeeRecipient() == nil {
-		err = pool.relay.HasPeerWithEtherbase(common.Address{})
-	} else {
-		err = pool.relay.HasPeerWithEtherbase(*tx.GatewayFeeRecipient())
-	}
-	if err != nil {
+	if err := pool.relay.HasPeerWithEtherbase(tx.GatewayFeeRecipient()); err != nil {
 		return err
 	}
 
```

### light/txpool_test.go
```diff
@@ -51,7 +51,7 @@ func (self *testTxRelay) Discard(hashes []common.Hash) {
 	self.discard <- len(hashes)
 }
 
-func (self *testTxRelay) HasPeerWithEtherbase(common.Address) error {
+func (self *testTxRelay) HasPeerWithEtherbase(*common.Address) error {
 	return nil
 }
 
```
