# [?] askrene: fix use-after-free if remove_htlc_min_violations fails.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-11-13
Source: https://github.com/ElementsProject/lightning/commit/e120202120a60ad82409915e004616f5af9f6cdc
Type: security-commit

## Details
askrene: fix use-after-free if remove_htlc_min_violations fails.

It can only fail on overflow, but if it did, the fail path frees working_ctx
and returns "error_message".

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### plugins/askrene/refine.c
```diff
@@ -506,7 +506,7 @@ const char *refine_flows(const tal_t *ctx, struct route_query *rq,
 		/* htlc_min is not met for this flow */
 		tal_arr_remove(&flows_index, i);
 		error_message = remove_htlc_min_violations(
-		    working_ctx, rq, (*flows)[k]);
+		    ctx, rq, (*flows)[k]);
 		if (error_message)
 			goto fail;
 	}
```
