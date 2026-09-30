# [?] connectd: fix exhaustion code where we pick random peer.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-05-13
Source: https://github.com/ElementsProject/lightning/commit/541cc9dd1f617ddc8e6a749010787e0338d3cf48
Type: security-commit

## Details
connectd: fix exhaustion code where we pick random peer.

If we don't find one searching from our random spot in the peer table,
we're supposed to wrap, not crash!

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### connectd/connectd.c
```diff
@@ -428,6 +428,8 @@ void close_random_connection(struct daemon *daemon)
 				break;
 		}
 		peer = peer_htable_next(daemon->peers, &it);
+		if (!peer)
+			peer = peer_htable_first(daemon->peers, &it);
 	}
 
 	if (best_peer) {
```
