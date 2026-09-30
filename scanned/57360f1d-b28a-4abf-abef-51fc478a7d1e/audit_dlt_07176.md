# [?] offers: fix crash when receiving response to offer without `offer_issuer_id`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-08-05
Source: https://github.com/ElementsProject/lightning/commit/8dbc1c5f2e70e590e2edb80b3af8df86d4c65236
Type: security-commit

## Details
offers: fix crash when receiving response to offer without `offer_issuer_id`

Now we actually check the other fields too, as per BOLT!

Reported-by: https://github.com/hMsats
Fixes: #7513
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### plugins/fetchinvoice.c
```diff
@@ -220,14 +220,38 @@ static struct command_result *handle_invreq_response(struct command *cmd,
 		goto badinv;
 	}
 
+	/* BOLT-offers #12:
+	 * A reader of an invoice:
+	 *   - MUST reject the invoice if `invoice_amount` is not present.
+	 *   - MUST reject the invoice if `invoice_created_at` is not present.
+	 *   - MUST reject the invoice if `invoice_payment_hash` is not present.
+	 *   - MUST reject the invoice if `invoice_node_id` is not present.
+	 */
+	if (!inv->invoice_amount) {
+		badfield = "invoice_amount";
+		goto badinv;
+	}
+	if (!inv->invoice_created_at) {
+		badfield = "invoice_amount";
+		goto badinv;
+	}
+	if (!inv->invoice_payment_hash) {
+		badfield = "invoice_payment_hash";
+		goto badinv;
+	}
+	if (!inv->invoice_node_id) {
+		badfield = "invoice_node_id";
+		goto badinv;
+	}
 	/* BOLT-offers #12:
 	 * - if `offer_issuer_id` is present (invoice_request for an offer):
 	 *   - MUST reject the invoice if `invoice_node_id` is not equal to `offer_issuer_id`
 	 * - otherwise, if `offer_paths` is present (invoice_request for an offer without id):
 	 *   - MUST reject the invoice if `invoice_node_id` is not equal to the final
 	 *    `blinded_node_id` it sent the `invoice_request` to.
 	 */
-	if (!inv->invoice_node_id || !pubkey_eq(inv->offer_issuer_id, sent->issuer_key)) {
+	/* Either way, we save the expected id in issuer_key */
+	if (!pubkey_eq(inv->invoice_node_id, sent->issuer_key)) {
 		badfield = "invoice_node_id";
 		goto badinv;
 	}
@@ -245,15 +269,6 @@ static struct command_result *handle_invreq_response(struct command *cmd,
 		goto badinv;
 	}
 
-	/* BOLT-offers #12:
-	 * A reader of an invoice:
-	 *   - MUST reject the invoice if `invoice_amount` is not present.
-	 */
-	if (!inv->invoice_amount) {
-		badfield = "invoice_amount";
-		goto badinv;
-	}
-
 	/* Get the amount we expected: firstly, if that's what we sent,
 	 * secondly, if specified in the invoice. */
 	if (inv->invreq_amount) {
```
