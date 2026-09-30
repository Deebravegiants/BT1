# [?] maybe_cleanup_forwarding: fix crash if payment_key not in self.received_mpp_htlcs

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2024-06-05
Source: https://github.com/spesmilo/electrum/commit/982443eaa3d866a2c9dee912cd4e233782f599d8
Type: security-commit

## Details
maybe_cleanup_forwarding: fix crash if payment_key not in self.received_mpp_htlcs

## Patch
### electrum/lnworker.py
```diff
@@ -2380,10 +2380,10 @@ def maybe_cleanup_forwarding(
         is_htlc_key = ':' in payment_key_hex
         if not is_htlc_key:
             payment_key = bytes.fromhex(payment_key_hex)
-            mpp_status = self.received_mpp_htlcs[payment_key]
-            if mpp_status.resolution == RecvMPPResolution.WAITING:
-                # reconstructing the MPP after restart
-                self.logger.info(f'cannot cleanup mpp, still waiting')
+            mpp_status = self.received_mpp_htlcs.get(payment_key)
+            if not mpp_status or mpp_status.resolution == RecvMPPResolution.WAITING:
+                # After restart, self.received_mpp_htlcs needs to be reconstructed
+                self.logger.info(f'maybe_cleanup_forwarding: mpp_status not ready')
                 return
             htlc_key = (short_channel_id, htlc)
             mpp_status.htlc_set.remove(htlc_key)  # side-effecting htlc_set
```
