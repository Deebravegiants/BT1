# [?] gossipd: fix crash in seeker rotation code.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-11-28
Source: https://github.com/ElementsProject/lightning/commit/9499d5c682cb76853b83c162e11430778eed579f
Type: security-commit

## Details
gossipd: fix crash in seeker rotation code.

Reported-by: hMsats
Fixes: https://github.com/ElementsProject/lightning/issues/7875
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>
Changelog-None: introduced in rc1

## Patch
### gossipd/seeker.c
```diff
@@ -904,7 +904,8 @@ static void reset_gossip_performance_metrics(struct seeker *seeker)
 {
 	seeker->new_gossiper_elapsed = 0;
 	for (int i = 0; i < tal_count(seeker->gossiper); i++) {
-		seeker->gossiper[i]->gossip_counter = 0;
+		if (seeker->gossiper[i])
+			seeker->gossiper[i]->gossip_counter = 0;
 	}
 }
 
```
