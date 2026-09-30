# [?] fix(taiko-client): remove ontake info in log to avoid panic (#18878)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2025-02-05
Source: https://github.com/taikoxyz/taiko-mono/commit/4a9202fffac67f14678a34daac6b0e6050fe7f64
Type: security-commit

## Details
fix(taiko-client): remove ontake info in log to avoid panic (#18878)

Co-authored-by: Gavin “yoghurt” Yu <guoyu960223@gmail.com>

## Patch
### packages/taiko-client/prover/prover.go
```diff
@@ -504,15 +504,13 @@ func (p *Prover) submitProofOp(proofResponse *proofProducer.ProofResponse) error
 			log.Error(
 				"Proof submission reverted",
 				"blockID", proofResponse.BlockID,
-				"minTier", proofResponse.Meta.Ontake().GetMinTier(),
 				"error", err,
 			)
 			return nil
 		}
 		log.Error(
 			"Submit proof error",
 			"blockID", proofResponse.BlockID,
-			"minTier", proofResponse.Meta.Ontake().GetMinTier(),
 			"error", err,
 		)
 		return err
```
