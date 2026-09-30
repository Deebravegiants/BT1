# [?] wallet: fix crash on listtransactions.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-05-27
Source: https://github.com/ElementsProject/lightning/commit/d3e33cfd14f904840ccd159dddd7a2a9d3874e3c
Type: security-commit

## Details
wallet: fix crash on listtransactions.

We removed the (experimental-only!) annotation output in 611795beee1bdecbde9e7b8c17db96d0934346be
but we still loaded them from the db.  Turns out that we were putting bogus
annotations into the db, and accessing out of range when loading them.

Consider the following db entry in transaction_annotations:

```
CREATE TABLE transaction_annotations (  txid BLOB, idx INTEGER, location INTEGER, type INTEGER, channel INTEGER REFERENCES channels(id), UNIQUE(txid, idx));
...
INSERT INTO transaction_annotations VALUES(X'19706f9af2875508a06c7db1754ef7ecb3da745ead005992e626441e4e83465f',18,1,129,53699);
```

Here is the corresponding entry in txs:

```
INSERT INTO transactions VALUES(X'19706f9af2875508a06c7db1754ef7ecb3da745ead005992e626441e4e83465f',710327,966,X'02000000000101f2add69112a1d557317826120e1f4ea3bc1cbe4674d720325695b26ecfe8355d120000000000000000013634000000000000160014dca21f104359bbb81e88ed7da985549f2cd0cbc30347304402201cdc854b76c4c7523e3ca09f38a81539d3b2f7fbd9a0de6ae10b7ceaa65ed9d402205a1770058cd1ef081c77c2fe957c07a334cb3a11bc0cc502834a29c59424fe010120589da1f809d955c7af150bf53123c27ffc0a741489b5291f6be811189863ec838576a9142f188d0d973c4ad1865a619d3748340b30746e088763ac672103b7bbcd592197ba6501e7176aabd3f908d94b126ae82ab1e7a4c58f5a789782e57c820120876475527c21029bcf62114eb36758fcb1aead7e67b6f707d32f34e67816894d5211ac9f2d6ce752ae67a9144483a115219ba65c63a3844be8445f739703bea988ac686800000000',NULL,NULL);
```

The annotation refers to output 18 of the tx, but it only has one output!

However, decoding the tx shows that it spent output 18 of a previous tx, so
that's probably where the `18` came from.

Remove this logic: we can remove the remaining (clearly broken!) annotation
adding code in another cleanup commit.

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### wallet/wallet.c
```diff
@@ -4809,11 +4809,7 @@ bool wallet_forward_delete(struct wallet *w,
 struct wallet_transaction *wallet_transactions_get(struct wallet *w, const tal_t *ctx)
 {
 	struct db_stmt *stmt;
-	struct wallet_transaction *cur = NULL, *txs = tal_arr(ctx, struct wallet_transaction, 0);
-	struct bitcoin_txid last;
-
-	/* Make sure we can check for changing txids */
-	memset(&last, 0, sizeof(last));
+	struct wallet_transaction *txs = tal_arr(ctx, struct wallet_transaction, 0);
 
 	stmt = db_prepare_v2(
 	    w->db,
@@ -4822,82 +4818,31 @@ struct wallet_transaction *wallet_transactions_get(struct wallet *w, const tal_t
 		", t.rawtx"
 		", t.blockheight"
 		", t.txindex"
-		", a.location"
-		", a.idx as ann_idx"
-		", a.type as annotation_type"
-		", c.scid"
 		" FROM"
 		"  transactions t LEFT JOIN"
-		"  transaction_annotations a ON (a.txid = t.id) LEFT JOIN"
-		"  channels c ON (a.channel = c.id) "
+		"  channels c ON (t.channel_id = c.id) "
 		"ORDER BY t.blockheight, t.txindex ASC"));
 	db_query_prepared(stmt);
 
 	while (db_step(stmt)) {
-		struct bitcoin_txid curtxid;
-		db_col_txid(stmt, "t.id", &curtxid);
-
-		/* If this is a new entry, allocate it in the array and set
-		 * the common fields (all fields from the transactions table. */
-		if (!bitcoin_txid_eq(&last, &curtxid)) {
-			last = curtxid;
-			tal_resize(&txs, tal_count(txs) + 1);
-			cur = &txs[tal_count(txs) - 1];
-			db_col_txid(stmt, "t.id", &cur->id);
-			cur->tx = db_col_tx(txs, stmt, "t.rawtx");
-			cur->rawtx = db_col_arr(txs, stmt, "t.rawtx", u8);
-			/* TX may be unconfirmed. */
-			if (!db_col_is_null(stmt, "t.blockheight")) {
-				cur->blockheight
-					= db_col_int(stmt, "t.blockheight");
-				if (!db_col_is_null(stmt, "t.txindex")) {
-					cur->txindex
-						= db_col_int(stmt, "t.txindex");
-				} else {
-					cur->txindex = 0;
-				}
+		struct wallet_transaction *cur;
+
+		tal_resize(&txs, tal_count(txs) + 1);
+		cur = &txs[tal_count(txs) - 1];
+		db_col_txid(stmt, "t.id", &cur->id);
+		cur->tx = db_col_tx(txs, stmt, "t.rawtx");
+		cur->rawtx = db_col_arr(txs, stmt, "t.rawtx", u8);
+		if (!db_col_is_null(stmt, "t.blockheight")) {
+			cur->blockheight = db_col_int(stmt, "t.blockheight");
+			if (!db_col_is_null(stmt, "t.txindex")) {
+				cur->txindex = db_col_int(stmt, "t.txindex");
 			} else {
-				db_col_ignore(stmt, "t.txindex");
-				cur->blockheight = 0;
 				cur->txindex = 0;
 			}
-			cur->output_annotations = tal_arrz(txs, struct tx_annotation, cur->tx->wtx->num_outputs);
-			cur->input_annotations = tal_arrz(txs, struct tx_annotation, cur->tx->wtx->num_inputs);
-		}
-
-		/* This should always be set by the above if-statement,
-		 * otherwise we have a txid of all 0x00 bytes... */
-		assert(cur != NULL);
-
-		/* Check if we have any annotations. If there are none the
-		 * fields are all set to null */
-		if (!db_col_is_null(stmt, "a.location")) {
-			enum wallet_tx_annotation_type loc
-				= db_col_int(stmt, "a.location");
-			int idx = db_col_int(stmt, "ann_idx");
-			struct tx_annotation *ann;
-
-			/* Select annotation from array to fill in. */
-			switch (loc) {
-			case OUTPUT_ANNOTATION:
-				ann = &cur->output_annotations[idx];
-				goto got_ann;
-			case INPUT_ANNOTATION:
-				ann = &cur->input_annotations[idx];
-				goto got_ann;
-			}
-			fatal("Transaction annotations are only available for inputs and outputs. Value %d", loc);
-
-		got_ann:
-			ann->type = db_col_int(stmt, "annotation_type");
-			if (!db_col_is_null(stmt, "c.scid"))
-				db_col_short_channel_id(stmt, "c.scid", &ann->channel);
-			else
-				ann->channel.u64 = 0;
 		} else {
-			db_col_ignore(stmt, "ann_idx");
-			db_col_ignore(stmt, "annotation_type");
-			db_col_ignore(stmt, "c.scid");
+			db_col_ignore(stmt, "t.txindex");
+			cur->blockheight = 0;
+			cur->txindex = 0;
 		}
 	}
 	tal_free(stmt);
```

### wallet/wallet.h
```diff
@@ -406,12 +406,6 @@ struct wallet_transaction {
 
 	/* Fully parsed transaction */
 	const struct bitcoin_tx *tx;
-
-	/* tal_arr containing the annotation types, if any, for the respective
-	 * inputs and outputs. 0 if there are no annotations for the
-	 * element. */
-	struct tx_annotation *input_annotations;
-	struct tx_annotation *output_annotations;
 };
 
 /**
```
