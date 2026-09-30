# [?] [panic] fix nil pointer crash during view change

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-03-08
Source: https://github.com/harmony-one/harmony/commit/61638240a2a42e850a3b81a0ee3ebf8039243ee6
Type: security-commit

## Details
[panic] fix nil pointer crash during view change

Signed-off-by: Leo Chen <leo@harmony.one>

## Patch
### consensus/view_change.go
```diff
@@ -258,14 +258,16 @@ func (consensus *Consensus) startViewChange() {
 	defer consensus.consensusTimeout[timeoutViewChange].Start()
 
 	// update the dictionary key if the viewID is first time received
-	consensus.vc.AddViewIDKeyIfNotExist(nextViewID, consensus.Decider.Participants())
+	members := consensus.Decider.Participants()
+	consensus.vc.AddViewIDKeyIfNotExist(nextViewID, members)
 
 	// init my own payload
 	if err := consensus.vc.InitPayload(
 		consensus.FBFTLog,
 		nextViewID,
 		consensus.blockNum,
-		consensus.priKey); err != nil {
+		consensus.priKey,
+		members); err != nil {
 		consensus.getLogger().Error().Err(err).Msg("[startViewChange] Init Payload Error")
 	}
 
@@ -387,7 +389,8 @@ func (consensus *Consensus) onViewChange(recvMsg *FBFTMessage) {
 	if err := consensus.vc.InitPayload(consensus.FBFTLog,
 		recvMsg.ViewID,
 		recvMsg.BlockNum,
-		consensus.priKey); err != nil {
+		consensus.priKey,
+		members); err != nil {
 		consensus.getLogger().Error().Err(err).Msg("[onViewChange] Init Payload Error")
 		return
 	}
```

### consensus/view_change_construct.go
```diff
@@ -348,6 +348,7 @@ func (vc *viewChange) InitPayload(
 	viewID uint64,
 	blockNum uint64,
 	privKeys multibls.PrivateKeys,
+	members multibls.PublicKeys,
 ) error {
 	// m1 or m2 init once per viewID/key.
 	// m1 and m2 are mutually exclusive.
@@ -376,10 +377,18 @@ func (vc *viewChange) InitPayload(
 					vc.getLogger().Info().Uint64("viewID", viewID).Uint64("blockNum", blockNum).Msg("[InitPayload] add my M1 (prepared) type messaage")
 					msgToSign := append(preparedMsg.BlockHash[:], preparedMsg.Payload...)
 					for _, key := range privKeys {
+						if _, ok := vc.bhpBitmap[viewID]; !ok {
+							// update the dictionary key if the viewID is first time received
+							bhpBitmap, _ := bls_cosi.NewMask(members, nil)
+							vc.bhpBitmap[viewID] = bhpBitmap
+						}
 						if err := vc.bhpBitmap[viewID].SetKey(key.Pub.Bytes, true); err != nil {
 							vc.getLogger().Warn().Str("key", key.Pub.Bytes.Hex()).Msg("[InitPayload] bhpBitmap setkey failed")
 							continue
 						}
+						if _, ok := vc.bhpSigs[viewID]; !ok {
+							vc.bhpSigs[viewID] = map[string]*bls_core.Sign{}
+						}
 						vc.bhpSigs[viewID][key.Pub.Bytes.Hex()] = key.Pri.SignHash(msgToSign)
 					}
 					hasBlock = true
@@ -393,6 +402,10 @@ func (vc *viewChange) InitPayload(
 		if !hasBlock {
 			vc.getLogger().Info().Uint64("viewID", viewID).Uint64("blockNum", blockNum).Msg("[InitPayload] add my M2 (NIL) type messaage")
 			for _, key := range privKeys {
+				if _, ok := vc.nilBitmap[viewID]; !ok {
+					nilBitmap, _ := bls_cosi.NewMask(members, nil)
+					vc.nilBitmap[viewID] = nilBitmap
+				}
 				if err := vc.nilBitmap[viewID].SetKey(key.Pub.Bytes, true); err != nil {
 					vc.getLogger().Warn().Str("key", key.Pub.Bytes.Hex()).Msg("[InitPayload] nilBitmap setkey failed")
 					continue
@@ -407,6 +420,9 @@ func (vc *viewChange) InitPayload(
 
 	inited = false
 	for _, key := range privKeys {
+		if _, ok := vc.viewIDSigs[viewID]; !ok {
+			vc.viewIDSigs[viewID] = map[string]*bls_core.Sign{}
+		}
 		_, ok3 := vc.viewIDSigs[viewID][key.Pub.Bytes.Hex()]
 		if ok3 {
 			inited = true
@@ -420,6 +436,10 @@ func (vc *viewChange) InitPayload(
 		binary.LittleEndian.PutUint64(viewIDBytes, viewID)
 		vc.getLogger().Info().Uint64("viewID", viewID).Uint64("blockNum", blockNum).Msg("[InitPayload] add my M3 (ViewID) type messaage")
 		for _, key := range privKeys {
+			if _, ok := vc.viewIDBitmap[viewID]; !ok {
+				viewIDBitmap, _ := bls_cosi.NewMask(members, nil)
+				vc.viewIDBitmap[viewID] = viewIDBitmap
+			}
 			if err := vc.viewIDBitmap[viewID].SetKey(key.Pub.Bytes, true); err != nil {
 				vc.getLogger().Warn().Str("key", key.Pub.Bytes.Hex()).Msg("[InitPayload] viewIDBitmap setkey failed")
 				continue
```
