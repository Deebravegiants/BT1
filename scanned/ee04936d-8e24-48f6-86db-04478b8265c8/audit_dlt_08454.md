# [?] fix(share/peer-manager): fix potential nil dereference in peer manager (#4117)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2025-02-13
Source: https://github.com/celestiaorg/celestia-node/commit/75dca6f294603a3231eb5c65cfda0c58b014d5ba
Type: security-commit

## Details
fix(share/peer-manager): fix potential nil dereference in peer manager (#4117)

## Patch
### share/shwap/p2p/shrex/peers/manager.go
```diff
@@ -286,7 +286,12 @@ func (m *Manager) doneFunc(datahash share.DataHash, peerID peer.ID, source peerS
 				m.nodes.putOnCooldown(peerID)
 				return
 			}
-			m.getPool(datahash.String()).putOnCooldown(peerID)
+			p := m.getPool(datahash.String())
+			if p == nil {
+				// pool was removed
+				return
+			}
+			p.putOnCooldown(peerID)
 		case ResultBlacklistPeer:
 			m.blacklistPeers(reasonMisbehave, peerID)
 		}
```
