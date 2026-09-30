# [?] htlc_wire: fix crash when adding an HTLC

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-08-26
Source: https://github.com/ElementsProject/lightning/commit/7e5cf41b4e5cd11064f3a8bcb63ec2edb2ea1dae
Type: security-commit

## Details
htlc_wire: fix crash when adding an HTLC

In line channeld/channeld_wiregen.c:832 `*added+i` is not a tal object hence
the instruction in common/htlc_wire.c:200 `tal_arr(ctx, struct tlv_field, 0);` crashes CLN.
This is fixed by stating that added_htlc is a a varsize_type.

Logs:

2025-08-16T02:25:28.640Z **BROKEN** lightningd: FATAL SIGNAL 6 (version v25.05-200-g79b959b)V
...
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:95 (call_error) 0x54f6bc
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:169 (check_bounds) 0x54f75a
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:178 (to_tal_hdr) 0x54f782
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:193 (to_tal_hdr_or_null) 0x54f7c7
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:471 (tal_alloc_) 0x54ffe4
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:517 (tal_alloc_arr_) 0x5500c4
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: common/htlc_wire.c:200 (fromwire_len_and_tlvstream) 0x48d63d
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: common/htlc_wire.c:234 (fromwire_added_htlc) 0x48dd23
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: channeld/channeld_wiregen.c:832 (fromwire_channeld_got_commitsig) 0x4c61fa
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/peer_htlcs.c:2377 (peer_got_commitsig) 0x4549cb
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/channel_control.c:1552 (channel_msg) 0x4140fe
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/subd.c:560 (sd_msg_read) 0x461513
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/io/io.c:60 (next_plan) 0x544885
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/io/io.c:422 (do_plan) 0x544cea
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/io/io.c:439 (io_ready) 0x544d9d
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/io/poll.c:455 (io_loop) 0x54665d
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/io_loop_with_timers.c:22 (io_loop_with_timers) 0x42d220
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/lightningd.c:1487 (main) 0x43280f

gdb inspection:
830             *added = num_added ? tal_arr(ctx, struct added_htlc, num_added) : NULL;
831             for (size_t i = 0; i < num_added; i++)
832                     fromwire_added_htlc(&cursor, &plen, *added + i);
(gdb) p i
$3 = 1

Changelog-None: crash introduced this release.
Signed-off-by: Lagrang3 <lagrang3@protonmail.com>
[ Added test, removed Changelog --RR ]

### channeld/channeld.c
```diff
@@ -1571,28 +1571,30 @@ static void marshall_htlc_info(const tal_t *ctx,
 			       struct changed_htlc **changed,
 			       struct fulfilled_htlc **fulfilled,
 			       const struct failed_htlc ***failed,
-			       struct added_htlc **added)
+			       const struct added_htlc ***added)
 {
 	*changed = tal_arr(ctx, struct changed_htlc, 0);
-	*added = tal_arr(ctx, struct added_htlc, 0);
+	*added = tal_arr(ctx, const struct added_htlc *, 0);
 	*failed = tal_arr(ctx, const struct failed_htlc *, 0);
 	*fulfilled = tal_arr(ctx, struct fulfilled_htlc, 0);
 
 	for (size_t i = 0; i < tal_count(changed_htlcs); i++) {
 		const struct htlc *htlc = changed_htlcs[i];
 		if (htlc->state == RCVD_ADD_COMMIT) {
-			struct added_htlc a;
+			struct added_htlc *a = tal(*added, struct added_htlc);
 
-			a.id = htlc->id;
-			a.amount = htlc->amount;
-			a.payment_hash = htlc->rhash;
-			a.cltv_expiry = abs_locktime_to_blocks(&htlc->expiry);
-			memcpy(a.onion_routing_packet,
+			a->id = htlc->id;
+			a->amount = htlc->amount;
+			a->payment_hash = htlc->rhash;
+			a->cltv_expiry = abs_locktime_to_blocks(&htlc->expiry);
+			memcpy(a->onion_routing_packet,
 			       htlc->routing,
-			       sizeof(a.onion_routing_packet));
-			a.path_key = htlc->path_key;
-			a.extra_tlvs = htlc->extra_tlvs;
-			a.fail_immediate = htlc->fail_immediate;
+			       sizeof(a->onion_routing_packet));
+			/* Note: we assume htlc's lifetime is greater than ours,
+			 * so we just share pointers and don't bother copying */
+			a->path_key = htlc->path_key;
+			a->extra_tlvs = htlc->extra_tlvs;
+			a->fail_immediate = htlc->fail_immediate;
 			tal_arr_expand(added, a);
 		} else if (htlc->state == RCVD_REMOVE_COMMIT) {
 			if (htlc->r) {
@@ -1629,7 +1631,7 @@ static void send_revocation(struct peer *peer,
 	struct changed_htlc *changed;
 	struct fulfilled_htlc *fulfilled;
 	const struct failed_htlc **failed;
-	struct added_htlc *added;
+	const struct added_htlc **added;
 	const u8 *msg;
 	const u8 *msg_for_master;
 
```

### common/htlc_wire.c
```diff
@@ -216,9 +216,10 @@ static struct tlv_field *fromwire_len_and_tlvstream(const tal_t *ctx,
 	return tlvs;
 }
 
-void fromwire_added_htlc(const u8 **cursor, size_t *max,
-			 struct added_htlc *added)
+struct added_htlc *fromwire_added_htlc(const tal_t *ctx, const u8 **cursor,
+				       size_t *max)
 {
+	struct added_htlc *added = tal(ctx, struct added_htlc);
 	added->id = fromwire_u64(cursor, max);
 	added->amount = fromwire_amount_msat(cursor, max);
 	fromwire_sha256(cursor, max, &added->payment_hash);
@@ -235,6 +236,7 @@ void fromwire_added_htlc(const u8 **cursor, size_t *max,
 	} else
 		added->extra_tlvs = NULL;
 	added->fail_immediate = fromwire_bool(cursor, max);
+	return added;
 }
 
 struct existing_htlc *fromwire_existing_htlc(const tal_t *ctx,
```

### common/htlc_wire.h
```diff
@@ -86,8 +86,8 @@ void towire_changed_htlc(u8 **pptr, const struct changed_htlc *changed);
 void towire_side(u8 **pptr, const enum side side);
 void towire_shachain(u8 **pptr, const struct shachain *shachain);
 
-void fromwire_added_htlc(const u8 **cursor, size_t *max,
-			 struct added_htlc *added);
+struct added_htlc *fromwire_added_htlc(const tal_t *ctx, const u8 **cursor,
+				       size_t *max);
 struct existing_htlc *fromwire_existing_htlc(const tal_t *ctx,
 					     const u8 **cursor, size_t *max);
 void fromwire_fulfilled_htlc(const u8 **cursor, size_t *max,
```

### lightningd/peer_htlcs.c
```diff
@@ -2309,15 +2309,15 @@ static bool channel_added_their_htlc(struct channel *channel,
 /* The peer doesn't tell us this separately, but logically it's a separate
  * step to receiving commitsig */
 static bool peer_sending_revocation(struct channel *channel,
-				    struct added_htlc *added,
+				    struct added_htlc **added,
 				    struct fulfilled_htlc *fulfilled,
 				    struct failed_htlc **failed,
 				    struct changed_htlc *changed)
 {
 	size_t i;
 
 	for (i = 0; i < tal_count(added); i++) {
-		if (!update_in_htlc(channel, added[i].id, SENT_ADD_REVOCATION))
+		if (!update_in_htlc(channel, added[i]->id, SENT_ADD_REVOCATION))
 			return false;
 	}
 	for (i = 0; i < tal_count(fulfilled); i++) {
@@ -2364,7 +2364,7 @@ void peer_got_commitsig(struct channel *channel, const u8 *msg)
 	struct fee_states *fee_states;
 	struct height_states *blockheight_states;
 	struct bitcoin_signature commit_sig, *htlc_sigs;
-	struct added_htlc *added;
+	struct added_htlc **added;
 	struct fulfilled_htlc *fulfilled;
 	struct failed_htlc **failed;
 	struct changed_htlc *changed;
@@ -2439,7 +2439,7 @@ void peer_got_commitsig(struct channel *channel, const u8 *msg)
 
 	/* New HTLCs */
 	for (i = 0; i < tal_count(added); i++) {
-		if (!channel_added_their_htlc(channel, &added[i]))
+		if (!channel_added_their_htlc(channel, added[i]))
 			return;
 	}
 
```

### tests/test_pay.py
```diff
@@ -7016,7 +7016,6 @@ def pay_with_sendonion(invoice, route, groupid, partid):
     assert invoice["amount_received_msat"] == Millisatoshi(total_amount)
 
 
-@pytest.mark.xfail(strict=True)
 def test_htlc_tlv_crash(node_factory):
     """Marshalling code treated an array of htlc_added as if they were tal objects, but only the head is a tal object so if we have more than one, BOOM!"""
     plugin = os.path.join(os.path.dirname(__file__), 'plugins/htlc_accepted-customtlv.py')
```

### tools/generate-wire.py
```diff
@@ -230,6 +230,7 @@ class Type(FieldSet):
         'gossip_getnodes_entry',
         'gossip_getchannels_entry',
         'failed_htlc',
+        'added_htlc',
         'existing_htlc',
         'inflight',
         'hsm_utxo',
```

### wallet/test/run-wallet.c
```diff
@@ -300,7 +300,7 @@ struct channel_type *fromwire_channel_type(const tal_t *ctx UNNEEDED, const u8 *
 bool fromwire_channeld_dev_memleak_reply(const void *p UNNEEDED, bool *leak UNNEEDED)
 { fprintf(stderr, "fromwire_channeld_dev_memleak_reply called!\n"); abort(); }
 /* Generated stub for fromwire_channeld_got_commitsig */
-bool fromwire_channeld_got_commitsig(const tal_t *ctx UNNEEDED, const void *p UNNEEDED, u64 *commitnum UNNEEDED, struct fee_states **fee_states UNNEEDED, struct height_states **blockheight_states UNNEEDED, struct bitcoin_signature *signature UNNEEDED, struct bitcoin_signature **htlc_signature UNNEEDED, struct added_htlc **added UNNEEDED, struct fulfilled_htlc **fulfilled UNNEEDED, struct failed_htlc ***failed UNNEEDED, struct changed_htlc **changed UNNEEDED, struct bitcoin_tx **tx UNNEEDED, struct commitsig ***inflight_commitsigs UNNEEDED)
+bool fromwire_channeld_got_commitsig(const tal_t *ctx UNNEEDED, const void *p UNNEEDED, u64 *commitnum UNNEEDED, struct fee_states **fee_states UNNEEDED, struct height_states **blockheight_states UNNEEDED, struct bitcoin_signature *signature UNNEEDED, struct bitcoin_signature **htlc_signature UNNEEDED, struct added_htlc ***added UNNEEDED, struct fulfilled_htlc **fulfilled UNNEEDED, struct failed_htlc ***failed UNNEEDED, struct changed_htlc **changed UNNEEDED, struct bitcoin_tx **tx UNNEEDED, struct commitsig ***inflight_commitsigs UNNEEDED)
 { fprintf(stderr, "fromwire_channeld_got_commitsig called!\n"); abort(); }
 /* Generated stub for fromwire_channeld_got_revoke */
 bool fromwire_channeld_got_revoke(const tal_t *ctx UNNEEDED, const void *p UNNEEDED, u64 *revokenum UNNEEDED, struct secret *per_commitment_secret UNNEEDED, struct pubkey *next_per_commit_point UNNEEDED, struct fee_states **fee_states UNNEEDED, struct height_states **blockheight_states UNNEEDED, struct changed_htlc **changed UNNEEDED, struct penalty_base **pbase UNNEEDED, struct bitcoin_tx **penalty_tx UNNEEDED)
```
