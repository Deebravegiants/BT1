# [?] offers: avoid potential expiry underflow when issuing invoices.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-08-20
Source: https://github.com/ElementsProject/lightning/commit/353b91c031bdb0761460fad0491ebf60d1291e94
Type: security-commit

## Details
offers: avoid potential expiry underflow when issuing invoices.

Issue #9378 notes that the absolute-expiry subtraction can underflow when an offer is already expired. Clamp that case to a one-second relative expiry so zero retains its cancellation meaning.

[ Added comment --RR ]

## Patch
### plugins/offers_invreq_hook.c
```diff
@@ -804,8 +804,18 @@ static struct command_result *handle_amount_and_recurrence(struct command *cmd,
 
 	/* Don't allow invoices past expiry of offer. */
 	if (ir->invreq->offer_absolute_expiry) {
-		u64 until = *ir->invreq->offer_absolute_expiry
-			- *ir->inv->invoice_created_at;
+		u64 until;
+
+		/* listoffers_done checked *ir->invreq->offer_absolute_expiry > now,
+		 * then invreq_for_invreq set *ir->inv->invoice_created_at = now.
+		 * Time could change between those, so set a minimum */
+		if (*ir->invreq->offer_absolute_expiry
+		    > *ir->inv->invoice_created_at)
+			until = *ir->invreq->offer_absolute_expiry
+				- *ir->inv->invoice_created_at;
+		else
+			/* Not 0: we use that for cancelled invoices! */
+			until = 1;
 		if (until < rel_expiry)
 			rel_expiry = until;
 	}
```
