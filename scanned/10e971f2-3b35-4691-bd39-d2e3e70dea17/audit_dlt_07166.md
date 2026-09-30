# [?] lightningd: fix crash on invoice_payment_hook_done

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-08-13
Source: https://github.com/ElementsProject/lightning/commit/f435096de2c7a1bbf91b452cbfd1105bd2ca452b
Type: security-commit

## Details
lightningd: fix crash on invoice_payment_hook_done

```
Valgrind error file: valgrind-errors.3449770
==3449770== Invalid read of size 8
==3449770==    at 0x1B4F4A: htlc_set_fail_ (htlc_set.c:77)
==3449770==    by 0x1B59FB: invoice_payment_hooks_done (invoice.c:276)
==3449770==    by 0x1EC5DF: hook_done (plugin_hook.c:243)
==3449770==    by 0x1EC710: plugin_hook_call_next (plugin_hook.c:343)
==3449770==    by 0x1EC90E: plugin_hook_callback (plugin_hook.c:299)
==3449770==    by 0x1E6316: plugin_response_handle (plugin.c:692)
==3449770==    by 0x1EB443: plugin_read_json (plugin.c:781)
==3449770==    by 0x283D01: next_plan (io.c:60)
==3449770==    by 0x28418C: do_plan (io.c:422)
==3449770==    by 0x284245: io_ready (io.c:439)
==3449770==    by 0x285BE3: io_loop (poll.c:471)
==3449770==    by 0x1B9A99: io_loop_with_timers (io_loop_with_timers.c:22)
==3449770==  Address 0x38 is not stack'd, malloc'd or (recently) free'd
==3449770==
{
   <insert_a_suppression_name_here>
   Memcheck:Addr8
   fun:htlc_set_fail_
   fun:invoice_payment_hooks_done
   fun:hook_done
   fun:plugin_hook_call_next
   fun:plugin_hook_callback
   fun:plugin_response_handle
   fun:plugin_read_json
   fun:next_plan
   fun:do_plan
   fun:io_ready
   fun:io_loop
   fun:io_loop_with_timers
}

```

Changelog-Fixed: lightningd: fix crash of lightningd on race condition between delinvoice and a returning invoice_payment hook for fallback onchain settlements

Reported-by: Vincenzo Palazzo (Bitcoin Security Council finding 2026-08-11)
Co-Authored-By: Grok 4.5
Signed-off-by: Lagrang3 <lagrang3@protonmail.com>

## Patch
### lightningd/invoice.c
```diff
@@ -273,7 +273,8 @@ invoice_payment_hooks_done(struct invoice_payment_hook_payload *payload STEALS)
 	/* If invoice gets paid meanwhile (plugin responds out-of-order?) then
 	 * we can also fail */
 	if (!invoices_find_by_label(ld->wallet->invoices, &inv_dbid, payload->label)) {
-		htlc_set_fail(payload->set, NULL);
+		if (payload->set)
+			htlc_set_fail(payload->set, NULL);
 		return;
 	}
 
```

### tests/test_invoices.py
```diff
@@ -888,6 +888,52 @@ def test_unified_invoices(node_factory, bitcoind):
     assert(txid == res['paid_outpoint']['txid'])
 
 
+def test_onchain_invoice_delinvoice_during_payment_hook(node_factory, bitcoind):
+    """delinvoice while onchain invoice_payment hook is pending must not crash."""
+    # Absolute path: inline plugins run in the test process (not lightning-dir).
+    unhold = [None]
+
+    def setup(plugin):
+        @plugin.hook("invoice_payment")
+        def on_payment(payment, plugin, **kwargs):
+            plugin.log("holding invoice_payment for label={}".format(payment["label"]))
+            while not os.path.exists(unhold[0]):
+                time.sleep(0.1)
+            plugin.log(
+                "releasing invoice_payment for label={}".format(payment["label"])
+            )
+            return {"result": "continue"}
+
+    l1 = node_factory.get_node(
+        options={"invoices-onchain-fallback": None}, inline_plugin=setup
+    )
+    unhold[0] = os.path.join(l1.daemon.lightning_dir, TEST_NETWORK, "unhold")
+    amount_sat = 1000
+    inv = l1.rpc.invoice(
+        amount_sat * 1000, "inv1", "test_onchain_invoice_delinvoice_during_payment_hook"
+    )
+    b11 = l1.rpc.decode(inv["bolt11"])
+    assert len(b11["fallbacks"]) == 1
+    addr = b11["fallbacks"][0]["addr"]
+
+    # Pay the on-chain fallback while the hook holds resolution.
+    bitcoind.rpc.sendtoaddress(addr, amount_sat / 10**8)
+    bitcoind.generate_block(1)
+
+    l1.daemon.wait_for_log(r"holding invoice_payment for label=inv1")
+    assert only_one(l1.rpc.listinvoices("inv1")["invoices"])["status"] == "unpaid"
+
+    # Delete the unpaid invoice while the hook is still pending.
+    l1.rpc.delinvoice("inv1", "unpaid")
+
+    # Let the hook finish; lightningd must survive the stale reply.
+    open(unhold[0], "w").close()
+    l1.daemon.wait_for_log(r"releasing invoice_payment for label=inv1")
+
+    # RPC still works => no restartable crash from invoice_payment_hooks_done.
+    assert l1.rpc.listinvoices("inv1") == {"invoices": []}
+
+
 def test_expiry_startup_crash(node_factory, bitcoind):
     """We crash trying to expire invoice on startup"""
     l1 = node_factory.get_node()
```
