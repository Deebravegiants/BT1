# [?] plugins/pay: fix crash if we try to self-pay a bolt12 invoice.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-07-09
Source: https://github.com/ElementsProject/lightning/commit/f64d48e7167c9da59db25b6b6d2fb7eae99e3d94
Type: security-commit

## Details
plugins/pay: fix crash if we try to self-pay a bolt12 invoice.

It doesn't work but at least now it doesn't crash!

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### plugins/pay.c
```diff
@@ -1217,6 +1217,9 @@ static struct command_result *json_pay(struct command *cmd,
 		else
 			invexpiry = *b12->invoice_created_at + BOLT12_DEFAULT_REL_EXPIRY;
 		p->local_invreq_id = tal_steal(p, local_invreq_id);
+
+		/* No payment secrets in bolt 12 (we use path_secret) */
+		p->payment_secret = NULL;
 	}
 
 	if (time_now().ts.tv_sec > invexpiry)
```
