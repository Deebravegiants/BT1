# [?] fix race condition when the AutoRelay peerChan fills up

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-04-10
Source: https://github.com/libp2p/go-libp2p/commit/46fc1e50825b6235d6a8edae07d1d07deb5debfa
Type: security-commit

## Details
fix race condition when the AutoRelay peerChan fills up

## Patch
### p2p/host/autorelay/autorelay.go
```diff
@@ -114,7 +114,10 @@ func (r *AutoRelay) background() {
 			case r.peerChanOut <- pi: // if there's space in the channel, great
 			default:
 				// no space left in the channel. Drop the oldest entry.
-				<-r.peerChanOut
+				select {
+				case <-r.peerChanOut:
+				default: // The consumer might just have emptied the channel. Make sure we don't block in that case.
+				}
 				r.peerChanOut <- pi
 			}
 		}
```
