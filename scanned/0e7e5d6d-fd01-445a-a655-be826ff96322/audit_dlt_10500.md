# [?] fix: sealing: Avoid nil dereference in debug log

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-12-09
Source: https://github.com/filecoin-project/lotus/commit/2871377cee8b174d0249682f5a730cbb833f41ac
Type: security-commit

## Details
fix: sealing: Avoid nil dereference in debug log

## Patch
### storage/pipeline/input.go
```diff
@@ -494,10 +494,6 @@ func (m *Sealing) updateInput(ctx context.Context, sp abi.RegisteredSealProof) e
 				continue
 			}
 			if !ok {
-				exp, _, _ := getExpirationCached(sector.number)
-
-				// todo move this log into checkDealAssignable, make more detailed about the reason
-				log.Debugf("CC update sector %d cannot fit deal, expiration %d before deal end epoch %d", id, exp, piece.deal.DealProposal.EndEpoch)
 				continue
 			}
 
```

### storage/pipeline/sealing.go
```diff
@@ -142,8 +142,21 @@ type openSector struct {
 }
 
 func (o *openSector) checkDealAssignable(piece *pendingPiece, expF expFn) (bool, error) {
+	log := log.With(
+		"sector", o.number,
+
+		"deal", piece.deal.DealID,
+		"dealEnd", piece.deal.DealProposal.EndEpoch,
+		"dealStart", piece.deal.DealProposal.StartEpoch,
+		"dealClaimEnd", piece.claimTerms.claimTermEnd,
+
+		"lastAssignedDealEnd", o.lastDealEnd,
+		"update", o.ccUpdate,
+	)
+
 	// if there are deals assigned, check that no assigned deal expires after termMax
 	if o.lastDealEnd > piece.claimTerms.claimTermEnd {
+		log.Debugw("deal not assignable to sector", "reason", "term end beyond last assigned deal end")
 		return false, nil
 	}
 
@@ -153,15 +166,26 @@ func (o *openSector) checkDealAssignable(piece *pendingPiece, expF expFn) (bool,
 	}
 	sectorExpiration, _, err := expF(o.number)
 	if err != nil {
+		log.Debugw("deal not assignable to sector", "reason", "error getting sector expiranion", "error", err)
 		return false, err
 	}
 
+	log = log.With(
+		"sectorExpiration", sectorExpiration,
+	)
+
 	// check that in case of upgrade sector, it's expiration isn't above deals claim TermMax
 	if sectorExpiration > piece.claimTerms.claimTermEnd {
+		log.Debugw("deal not assignable to sector", "reason", "term end beyond sector expiration")
+		return false, nil
+	}
+
+	if sectorExpiration < piece.deal.DealProposal.EndEpoch {
+		log.Debugw("deal not assignable to sector", "reason", "sector expiration less than deal expiration")
 		return false, nil
 	}
 
-	return sectorExpiration >= piece.deal.DealProposal.EndEpoch, nil
+	return true, nil
 }
 
 type pieceAcceptResp struct {
```
