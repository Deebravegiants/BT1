# [?] Fix race condition where p2p is faster than ETH

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2020-08-20
Source: https://github.com/wormhole-foundation/wormhole/commit/b6b2d21bde7f1e0020f1f05c0019e48e4d6d0ac8
Type: security-commit

## Details
Fix race condition where p2p is faster than ETH

## Patch
### bridge/cmd/guardiand/ethwatch.go
```diff
@@ -222,53 +222,56 @@ func ethLockupProcessor(lockC chan *common.ChainLock, setC chan *common.Guardian
 					agg[i] = ok
 				}
 
-				// Deep copy the VAA and add signatures
-				v := state.lockupSignatures[hash].ourVAA
-				signed := &vaa.VAA{
-					Version:          v.Version,
-					GuardianSetIndex: v.GuardianSetIndex,
-					Signatures:       sigs,
-					Timestamp:        v.Timestamp,
-					Payload:          v.Payload,
-				}
+				if state.lockupSignatures[hash].ourVAA != nil {
+					// We have seen it on chain!
+					// Deep copy the VAA and add signatures
+					v := state.lockupSignatures[hash].ourVAA
+					signed := &vaa.VAA{
+						Version:          v.Version,
+						GuardianSetIndex: v.GuardianSetIndex,
+						Signatures:       sigs,
+						Timestamp:        v.Timestamp,
+						Payload:          v.Payload,
+					}
 
-				// 2/3+ majority required for VAA to be valid - wait until we have quorum to submit VAA.
-				quorum := int(math.Ceil((float64(len(gs.Keys)) / 3) * 2))
+					// 2/3+ majority required for VAA to be valid - wait until we have quorum to submit VAA.
+					quorum := int(math.Ceil((float64(len(gs.Keys)) / 3) * 2))
 
-				logger.Info("aggregation state for eth lockup",
-					zap.String("vaahash", hash),
-					zap.Any("set", gs.KeysAsHexStrings()),
-					zap.Uint32("index", gs.Index),
-					zap.Bools("aggregation", agg),
-					zap.Int("required_sigs", quorum),
-					zap.Int("have_sigs", len(sigs)),
-					)
+					logger.Info("aggregation state for eth lockup",
+						zap.String("vaahash", hash),
+						zap.Any("set", gs.KeysAsHexStrings()),
+						zap.Uint32("index", gs.Index),
+						zap.Bools("aggregation", agg),
+						zap.Int("required_sigs", quorum),
+						zap.Int("have_sigs", len(sigs)),
+						)
+
+					if *unsafeDevMode && len(sigs) >= quorum {
+						_, err := devnet.GetDevnetIndex()
+						if err != nil {
+							return err
+						}
 
-				if *unsafeDevMode && len(sigs) >= quorum {
-					_, err := devnet.GetDevnetIndex()
-					if err != nil {
-						return err
-					}
+						vaaBytes, err := signed.Marshal()
+						if err != nil {
+							panic(err)
+						}
 
-					vaaBytes, err := signed.Marshal()
-					if err != nil {
-						panic(err)
+						logger.Info("submitting signed VAA to Solana",
+							zap.String("vaahash", hash),
+							zap.Any("vaa", signed),
+							zap.Binary("bytes", vaaBytes))
+
+						// TODO: actually submit to Solana once the agent works and has a reasonable key
+						//if idx == 0 {
+						//	vaaC <- state.lockupSignatures[hash].ourVAA
+						//}
+					} else if !*unsafeDevMode {
+						panic("not implemented")  // TODO
+					} else {
+						logger.Info("quorum not met, doing nothing",
+							zap.String("vaahash", hash))
 					}
-
-					logger.Info("submitting signed VAA to Solana",
-						zap.String("vaahash", hash),
-						zap.Any("vaa", signed),
-						zap.Binary("bytes", vaaBytes))
-
-					// TODO: actually submit to Solana once the agent works and has a reasonable key
-					//if idx == 0 {
-					//	vaaC <- state.lockupSignatures[hash].ourVAA
-					//}
-				} else if !*unsafeDevMode {
-					panic("not implemented")  // TODO
-				} else {
-					logger.Info("quorum not met, doing nothing",
-						zap.String("vaahash", hash))
 				}
 			}
 		}
```
