# [?] peer: fix panic due to err in handleVersionMsg

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2015-12-09
Source: https://github.com/btcsuite/btcd/commit/542844832e6eccbce6c0650ba5d244562c60e09b
Type: security-commit

## Details
peer: fix panic due to err in handleVersionMsg

In case of an error during protocol negotiation in handleVersionMsg,
immediately break out and prevent further processing of OnVersion
listener which generally depends upon peer attributes like NA to be set
during the negotiation. Fixes #579.

## Patch
### peer/peer.go
```diff
@@ -7,6 +7,7 @@ package peer
 import (
 	"bytes"
 	"container/list"
+	"errors"
 	"fmt"
 	"io"
 	prand "math/rand"
@@ -974,12 +975,10 @@ func (p *Peer) PushRejectMsg(command string, code wire.RejectCode, reason string
 // handleVersionMsg is invoked when a peer receives a version bitcoin message
 // and is used to negotiate the protocol version details as well as kick start
 // the communications.
-func (p *Peer) handleVersionMsg(msg *wire.MsgVersion) {
+func (p *Peer) handleVersionMsg(msg *wire.MsgVersion) error {
 	// Detect self connections.
 	if !allowSelfConns && sentNonces.Exists(msg.Nonce) {
-		log.Debugf("Disconnecting peer connected to self %s", p)
-		p.Disconnect()
-		return
+		return errors.New("disconnecting peer connected to self")
 	}
 
 	// Notify and disconnect clients that have a protocol version that is
@@ -992,25 +991,19 @@ func (p *Peer) handleVersionMsg(msg *wire.MsgVersion) {
 			wire.MultipleAddressVersion)
 		p.PushRejectMsg(msg.Command(), wire.RejectObsolete, reason,
 			nil, true)
-		p.Disconnect()
-		return
+		return errors.New(reason)
 	}
 
 	// Limit to one version message per peer.
 	// No read lock is necessary because versionKnown is not written to in any
 	// other goroutine
 	if p.versionKnown {
-		log.Errorf("Only one version message per peer is allowed %s.",
-			p)
-
 		// Send an reject message indicating the version message was
 		// incorrectly sent twice and wait for the message to be sent
 		// before disconnecting.
 		p.PushRejectMsg(msg.Command(), wire.RejectDuplicate,
 			"duplicate version message", nil, true)
-
-		p.Disconnect()
-		return
+		return errors.New("only one version message per peer is allowed")
 	}
 
 	// Updating a bunch of stats.
@@ -1043,24 +1036,20 @@ func (p *Peer) handleVersionMsg(msg *wire.MsgVersion) {
 		// at connection time and no point recomputing.
 		na, err := newNetAddress(p.conn.RemoteAddr(), p.services)
 		if err != nil {
-			log.Errorf("Can't get remote address: %v", err)
-			p.Disconnect()
-			return
+			return err
 		}
 		p.na = na
 
 		// Send version.
 		err = p.pushVersionMsg()
 		if err != nil {
-			log.Errorf("Can't send version message to %s: %v",
-				p, err)
-			p.Disconnect()
-			return
+			return err
 		}
 	}
 
 	// Send verack.
 	p.QueueMessage(wire.NewMsgVerAck(), nil)
+	return nil
 }
 
 // isValidBIP0111 is a helper function for the bloom filter commands to check
@@ -1527,7 +1516,13 @@ out:
 		p.stallControl <- stallControlMsg{sccHandlerStart, rmsg}
 		switch msg := rmsg.(type) {
 		case *wire.MsgVersion:
-			p.handleVersionMsg(msg)
+			err := p.handleVersionMsg(msg)
+			if err != nil {
+				log.Debugf("New peer %v - error negotiating protocol: %v",
+					p, err)
+				p.Disconnect()
+				break out
+			}
 			if p.cfg.Listeners.OnVersion != nil {
 				p.cfg.Listeners.OnVersion(p, msg)
 			}
```
