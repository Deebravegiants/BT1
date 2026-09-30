# [?] [panic] fix nil pointer map assignment

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-03-08
Source: https://github.com/harmony-one/harmony/commit/b3cab12851c32f78b5bca98c93eeeec5b9b859d5
Type: security-commit

## Details
[panic] fix nil pointer map assignment

add further protection to vc map assignment

Signed-off-by: Leo Chen <leo@harmony.one>

## Patch
### consensus/view_change_construct.go
```diff
@@ -285,14 +285,30 @@ func (vc *viewChange) ProcessViewChangeMsg(
 		vc.getLogger().Info().Uint64("viewID", recvMsg.ViewID).
 			Str("validatorPubKey", senderKeyStr).
 			Msg("[ProcessViewChangeMsg] Add M1 (prepared) type message")
+
+		if _, ok := vc.bhpSigs[recvMsg.ViewID]; !ok {
+			vc.bhpSigs[recvMsg.ViewID] = map[string]*bls_core.Sign{}
+		}
 		vc.bhpSigs[recvMsg.ViewID][senderKeyStr] = recvMsg.ViewchangeSig
+		if _, ok := vc.bhpBitmap[recvMsg.ViewID]; !ok {
+			bhpBitmap, _ := bls_cosi.NewMask(decider.Participants(), nil)
+			vc.bhpBitmap[recvMsg.ViewID] = bhpBitmap
+		}
 		vc.bhpBitmap[recvMsg.ViewID].SetKey(senderKey.Bytes, true) // Set the bitmap indicating that this validator signed.
 
 		vc.getLogger().Info().Uint64("viewID", recvMsg.ViewID).
 			Str("validatorPubKey", senderKeyStr).
 			Msg("[ProcessViewChangeMsg] Add M3 (ViewID) type message")
 
+		if _, ok := vc.viewIDSigs[recvMsg.ViewID]; !ok {
+			vc.viewIDSigs[recvMsg.ViewID] = map[string]*bls_core.Sign{}
+		}
 		vc.viewIDSigs[recvMsg.ViewID][senderKeyStr] = recvMsg.ViewidSig
+
+		if _, ok := vc.viewIDBitmap[recvMsg.ViewID]; !ok {
+			viewIDBitmap, _ := bls_cosi.NewMask(decider.Participants(), nil)
+			vc.viewIDBitmap[recvMsg.ViewID] = viewIDBitmap
+		}
 		// Set the bitmap indicating that this validator signed.
 		vc.viewIDBitmap[recvMsg.ViewID].SetKey(senderKey.Bytes, true)
 
@@ -328,15 +344,32 @@ func (vc *viewChange) ProcessViewChangeMsg(
 	vc.getLogger().Info().Uint64("viewID", recvMsg.ViewID).
 		Str("validatorPubKey", senderKeyStr).
 		Msg("[ProcessViewChangeMsg] Add M2 (NIL) type message")
+
+	if _, ok := vc.nilSigs[recvMsg.ViewID]; !ok {
+		vc.nilSigs[recvMsg.ViewID] = map[string]*bls_core.Sign{}
+	}
 	vc.nilSigs[recvMsg.ViewID][senderKeyStr] = recvMsg.ViewchangeSig
+
+	if _, ok := vc.nilBitmap[recvMsg.ViewID]; !ok {
+		nilBitmap, _ := bls_cosi.NewMask(decider.Participants(), nil)
+		vc.nilBitmap[recvMsg.ViewID] = nilBitmap
+	}
 	vc.nilBitmap[recvMsg.ViewID].SetKey(senderKey.Bytes, true) // Set the bitmap indicating that this validator signed.
 
 	vc.getLogger().Info().Uint64("viewID", recvMsg.ViewID).
 		Str("validatorPubKey", senderKeyStr).
 		Msg("[ProcessViewChangeMsg] Add M3 (ViewID) type message")
 
+	if _, ok := vc.viewIDSigs[recvMsg.ViewID]; !ok {
+		vc.viewIDSigs[recvMsg.ViewID] = map[string]*bls_core.Sign{}
+	}
 	vc.viewIDSigs[recvMsg.ViewID][senderKeyStr] = recvMsg.ViewidSig
+
 	// Set the bitmap indicating that this validator signed.
+	if _, ok := vc.viewIDBitmap[recvMsg.ViewID]; !ok {
+		viewIDBitmap, _ := bls_cosi.NewMask(decider.Participants(), nil)
+		vc.viewIDBitmap[recvMsg.ViewID] = viewIDBitmap
+	}
 	vc.viewIDBitmap[recvMsg.ViewID].SetKey(senderKey.Bytes, true)
 
 	return nil
@@ -377,8 +410,8 @@ func (vc *viewChange) InitPayload(
 					vc.getLogger().Info().Uint64("viewID", viewID).Uint64("blockNum", blockNum).Msg("[InitPayload] add my M1 (prepared) type messaage")
 					msgToSign := append(preparedMsg.BlockHash[:], preparedMsg.Payload...)
 					for _, key := range privKeys {
+						// update the dictionary key if the viewID is first time received
 						if _, ok := vc.bhpBitmap[viewID]; !ok {
-							// update the dictionary key if the viewID is first time received
 							bhpBitmap, _ := bls_cosi.NewMask(members, nil)
 							vc.bhpBitmap[viewID] = bhpBitmap
 						}
@@ -420,9 +453,6 @@ func (vc *viewChange) InitPayload(
 
 	inited = false
 	for _, key := range privKeys {
-		if _, ok := vc.viewIDSigs[viewID]; !ok {
-			vc.viewIDSigs[viewID] = map[string]*bls_core.Sign{}
-		}
 		_, ok3 := vc.viewIDSigs[viewID][key.Pub.Bytes.Hex()]
 		if ok3 {
 			inited = true
```
