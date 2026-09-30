# [?] qt: fix crash through stale pi resolve

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2026-07-01
Source: https://github.com/spesmilo/electrum/commit/299be4105e6216b56fc465ba6905f69912be4cf0
Type: security-commit

## Details
qt: fix crash through stale pi resolve

When multiple PIs get resolved consecutively through
repeated editing of the PI field, and the `on_resolve_done`
callback tries to access a PI that has been cleared by
a previous, failed callback an exception is raised.

I was able to reproduce this somehow by adding a sleep to
`PaymentIdentifier._do_resolve()` and entering lightning addresses.

Fixes https://github.com/spesmilo/electrum/issues/10724

## Patch
### electrum/gui/qt/send_tab.py
```diff
@@ -493,6 +493,10 @@ def _handle_payment_identifier(self):
     def on_resolve_done(self, pi: 'PaymentIdentifier'):
         # TODO: resolve can happen while typing, we don't want message dialogs to pop up
         # currently we don't set error for emaillike recipients to avoid just that
+        if pi != self.payto_e.payment_identifier:
+            self.logger.debug(f"stale resolve done")
+            return
+
         self.logger.debug('payment identifier resolve done')
         self.spinner.setVisible(False)
         if pi.error:
```
