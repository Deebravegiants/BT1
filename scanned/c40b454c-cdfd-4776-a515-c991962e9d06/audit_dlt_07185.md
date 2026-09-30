# [?] lightningd: fix crash on startup expirations.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-07-31
Source: https://github.com/ElementsProject/lightning/commit/2c2592fe366b8cb31de7242acf4be5cb59d6f7ab
Type: security-commit

## Details
lightningd: fix crash on startup expirations.

The wait code assumes ld->wallet is populated, but it's not.  Start the
expiration cycle later.

```
0x7f271a18d08f ??? /build/glibc-SzIz7B/glibc-2.31/signal/../sysdeps/unix/sysv/linux/x86_64/sigaction.c:0
0x5581a27dc082 wait_index_increment lightningd/wait.c:112
0x5581a27e331a invoice_index_inc wallet/invoices.c:738
0x5581a27e3dfe invoice_index_update_status wallet/invoices.c:775
0x5581a27e3ea3 trigger_expiration wallet/invoices.c:185
0x5581a27e3f47 invoices_new wallet/invoices.c:134
0x5581a27e8a2c wallet_new wallet/wallet.c:121
0x5581a27b08b5 main lightningd/lightningd.c:1082
```

Fixes: #6457
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/lightningd.c
```diff
@@ -77,6 +77,7 @@
 #include <lightningd/runes.h>
 #include <lightningd/subd.h>
 #include <sys/resource.h>
+#include <wallet/invoices.h>
 #include <wallet/txfilter.h>
 #include <wally_bip32.h>
 
@@ -1192,6 +1193,9 @@ int main(int argc, char *argv[])
 	/*~ Finish our runes initialization (includes reading from db) */
 	runes_finish_init(ld->runes);
 
+	/*~ Start expiring old invoices now ld->wallet is set.*/
+	invoices_start_expiration(ld);
+
 	/*~ That's all of the wallet db operations for now. */
 	db_commit_transaction(ld->wallet->db);
 
```

### lightningd/test/run-find_my_abspath.c
```diff
@@ -114,6 +114,9 @@ void htlcs_notify_new_block(struct lightningd *ld UNNEEDED, u32 height UNNEEDED)
 void htlcs_resubmit(struct lightningd *ld UNNEEDED,
 		    struct htlc_in_map *unconnected_htlcs_in STEALS UNNEEDED)
 { fprintf(stderr, "htlcs_resubmit called!\n"); abort(); }
+/* Generated stub for invoices_start_expiration */
+void invoices_start_expiration(struct lightningd *ld UNNEEDED)
+{ fprintf(stderr, "invoices_start_expiration called!\n"); abort(); }
 /* Generated stub for json_add_string */
 void json_add_string(struct json_stream *js UNNEEDED,
 		     const char *fieldname UNNEEDED,
```

### tests/test_invoices.py
```diff
@@ -913,7 +913,6 @@ def test_listinvoices_index(node_factory, executor):
         assert only_one(l2.rpc.listinvoices(index='updated', start=i, limit=1)['invoices'])['label'] == str(70 + 1 - i)
 
 
-@pytest.mark.xfail(strict=True)
 def test_expiry_startup_crash(node_factory, bitcoind):
     """We crash trying to expire invoice on startup"""
     l1 = node_factory.get_node()
```

### wallet/invoices.c
```diff
@@ -6,6 +6,7 @@
 #include <db/exec.h>
 #include <db/utils.h>
 #include <lightningd/invoice.h>
+#include <lightningd/lightningd.h>
 #include <lightningd/wait.h>
 #include <wallet/invoices.h>
 
@@ -115,7 +116,6 @@ static struct invoice_details *wallet_stmt2invoice_details(const tal_t *ctx,
 	return dtl;
 }
 
-static void trigger_expiration(struct invoices *invoices);
 static void install_expiration_timer(struct invoices *invoices);
 
 struct invoices *invoices_new(const tal_t *ctx,
@@ -130,8 +130,6 @@ struct invoices *invoices_new(const tal_t *ctx,
 	list_head_init(&invs->waiters);
 
 	invs->expiration_timer = NULL;
-
-	trigger_expiration(invs);
 	return invs;
 }
 
@@ -784,3 +782,8 @@ u64 invoice_index_update_deldesc(struct lightningd *ld,
 	return invoice_index_inc(ld, NULL, label, NULL, description,
 				 WAIT_INDEX_UPDATED);
 }
+
+void invoices_start_expiration(struct lightningd *ld)
+{
+	trigger_expiration(ld->wallet->invoices);
+}
```

### wallet/invoices.h
```diff
@@ -26,6 +26,13 @@ struct invoices *invoices_new(const tal_t *ctx,
 			      struct wallet *wallet,
 			      struct timers *timers);
 
+/**
+ * invoices_start_expiration - Once ld->wallet complete, we can start expiring.
+ *
+ * @ld - the lightningd object
+ */
+void invoices_start_expiration(struct lightningd *ld);
+
 /**
  * invoices_create - Create a new invoice.
  *
```
