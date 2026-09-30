# [?] [panic] fix a panic in view change

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-03-01
Source: https://github.com/harmony-one/harmony/commit/52dbcf1d11b0e1fc5033689489cc5d700f6b5bea
Type: security-commit

## Details
[panic] fix a panic in view change

This PR fixes the un-initialized map panic found in the following issue.
https://github.com/harmony-one/harmony/issues/3557

Signed-off-by: Leo Chen <leo@harmony.one>

## Patch
### consensus/view_change_construct.go
```diff
@@ -397,6 +397,9 @@ func (vc *viewChange) InitPayload(
 					vc.getLogger().Warn().Str("key", key.Pub.Bytes.Hex()).Msg("[InitPayload] nilBitmap setkey failed")
 					continue
 				}
+				if _, ok := vc.nilSigs[viewID]; !ok {
+					vc.nilSigs[viewID] = map[string]*bls_core.Sign{}
+				}
 				vc.nilSigs[viewID][key.Pub.Bytes.Hex()] = key.Pri.SignHash(NIL)
 			}
 		}
@@ -421,6 +424,9 @@ func (vc *viewChange) InitPayload(
 				vc.getLogger().Warn().Str("key", key.Pub.Bytes.Hex()).Msg("[InitPayload] viewIDBitmap setkey failed")
 				continue
 			}
+			if _, ok := vc.viewIDSigs[viewID]; !ok {
+				vc.viewIDSigs[viewID] = map[string]*bls_core.Sign{}
+			}
 			vc.viewIDSigs[viewID][key.Pub.Bytes.Hex()] = key.Pri.SignHash(viewIDBytes)
 		}
 	}
```
