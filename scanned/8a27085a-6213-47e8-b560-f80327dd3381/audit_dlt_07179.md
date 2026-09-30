# [?] lightningd: avoid crash from hsmd not signing anchor spend

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-05-07
Source: https://github.com/ElementsProject/lightning/commit/c3280676e8a461374ca5854aa50e587d5532c7e8
Type: security-commit

## Details
lightningd: avoid crash from hsmd not signing anchor spend

Temporary patch to avoid issue #6973

[ Add much more logging! --RR ]

Changelog-Fixed: lightningd: avoid crash on signing failure when trying to spend anchor outputs.

## Patch
### lightningd/anchorspend.c
```diff
@@ -266,7 +266,7 @@ static struct bitcoin_tx *spend_anchor(const tal_t *ctx,
 	size_t base_weight, weight;
 	struct amount_sat fee, diff;
 	struct bitcoin_tx *tx;
-	struct wally_psbt *psbt;
+	struct wally_psbt *psbt, *signed_psbt;
 	struct amount_msat total_value;
 	const u8 *msg;
 
@@ -381,21 +381,44 @@ static struct bitcoin_tx *spend_anchor(const tal_t *ctx,
 						       utxos),
 					   psbt);
 	msg = hsm_sync_req(tmpctx, ld, take(msg));
-	if (!fromwire_hsmd_sign_anchorspend_reply(tmpctx, msg, &psbt))
+	if (!fromwire_hsmd_sign_anchorspend_reply(tmpctx, msg, &signed_psbt))
 		fatal("Reading sign_anchorspend_reply: %s", tal_hex(tmpctx, msg));
 
-	if (!psbt_finalize(psbt))
-		fatal("Non-final PSBT from hsm: %s",
-		      fmt_wally_psbt(tmpctx, psbt));
+	if (!psbt_finalize(signed_psbt)) {
+		/* Lots of logging, to try to figure out why! */
+		log_broken(channel->log, "Non-final PSBT from hsm: %s",
+			   fmt_wally_psbt(tmpctx, signed_psbt));
+		log_broken(channel->log, "Before signing PSBT was %s",
+			   fmt_wally_psbt(tmpctx, psbt));
+		for (size_t i = 0; i < tal_count(utxos); i++) {
+			const struct unilateral_close_info *ci = utxos[i]->close_info;
+
+			log_broken(channel->log, "UTXO %zu: %s amt=%s keyidx=%u",
+				   i,
+				   fmt_bitcoin_outpoint(tmpctx, &utxos[i]->outpoint),
+				   fmt_amount_sat(tmpctx, utxos[i]->amount),
+				   utxos[i]->keyindex);
+			if (ci) {
+				log_broken(channel->log,
+					   "... close from channel %"PRIu64" peer %s (%s) commitment %s csv %u",
+					   ci->channel_id,
+					   fmt_node_id(tmpctx, &ci->peer_id),
+					   ci->option_anchors ? "anchor" : "non-anchor",
+					   ci->commitment_point ? fmt_pubkey(tmpctx, ci->commitment_point) : "none",
+					   ci->csv);
+			}
+		}
+		return NULL;
+	}
 
 	/* Update fee so we know for next time */
 	anch->anchor_spend_fee = fee;
 
 	tx = tal(ctx, struct bitcoin_tx);
 	tx->chainparams = chainparams;
-	tx->wtx = psbt_final_tx(tx, psbt);
+	tx->wtx = psbt_final_tx(tx, signed_psbt);
 	assert(tx->wtx);
-	tx->psbt = tal_steal(tx, psbt);
+	tx->psbt = tal_steal(tx, signed_psbt);
 
 	return tx;
 }
```
