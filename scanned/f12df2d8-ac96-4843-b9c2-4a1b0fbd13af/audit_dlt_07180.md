# [?] lightningd: fix name for deprecated APIs, and fix crash with listconfigs when --i-promise-to-fix-broken-api-user is used.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-03-25
Source: https://github.com/ElementsProject/lightning/commit/ed4af14d4c11d57a19153fad2532db02f5084c8c
Type: security-commit

## Details
lightningd: fix name for deprecated APIs, and fix crash with listconfigs when --i-promise-to-fix-broken-api-user is used.

We were duplicating the command name (e.g. "autocleaninvoice.autocleaninvoice"), and also not
handling listconfigs if they specified the (currently unused!) i-promise-to-fix-broken-api-user
option, which we are going to use next patch.

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/jsonrpc.c
```diff
@@ -1157,8 +1157,7 @@ parse_request(struct json_connection *jcon, const jsmntok_t tok[])
 		    c, JSONRPC2_METHOD_NOT_FOUND, "Unknown command '%.*s'",
 		    method->end - method->start, jcon->buffer + method->start);
 	}
-	if (!command_deprecated_in_ok(c,
-				      json_strdup(tmpctx, jcon->buffer, method),
+	if (!command_deprecated_in_ok(c, NULL,
 				      c->json_cmd->depr_start,
 				      c->json_cmd->depr_end)) {
 		return command_fail(c, JSONRPC2_METHOD_NOT_FOUND,
```

### lightningd/options.c
```diff
@@ -2182,6 +2182,7 @@ bool is_known_opt_cb_arg(char *(*cb_arg)(const char *, void *))
 		|| cb_arg == (void *)opt_add_accept_htlc_tlv
 		|| cb_arg == (void *)opt_set_codex32_or_hex
 		|| cb_arg == (void *)opt_subd_dev_disconnect
+		|| cb_arg == (void *)opt_add_api_beg
 		|| cb_arg == (void *)opt_force_featureset
 		|| cb_arg == (void *)opt_force_privkey
 		|| cb_arg == (void *)opt_force_bip32_seed
```

### tests/test_invoices.py
```diff
@@ -574,6 +574,9 @@ def test_autocleaninvoice_deprecated(node_factory):
     l1.rpc.invoice(amount_msat=12300, label='inv1', description='description1', expiry=4)
     l1.rpc.invoice(amount_msat=12300, label='inv2', description='description2', expiry=12)
     l1.rpc.autocleaninvoice(cycle_seconds=8, expired_by=2)
+
+    # Should log the correct name of the API
+    l1.daemon.wait_for_log(r"\*\*BROKEN\*\* jsonrpc#[0-9]*: DEPRECATED API USED autocleaninvoice ")
     start_time = time.time()
 
     # time 0
```
