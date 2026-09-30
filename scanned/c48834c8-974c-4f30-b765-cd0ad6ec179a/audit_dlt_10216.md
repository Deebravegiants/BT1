# [?] use saturation_add to prevent panic

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-12-05
Source: https://github.com/penumbra-zone/penumbra/commit/17ac02a9ffce11d933eb2a7ddcb0abd71f01012e
Type: security-commit

## Details
use saturation_add to prevent panic

## Patch
### crates/core/component/shielded-pool/src/component/transfer.rs
```diff
@@ -381,7 +381,7 @@ async fn recv_transfer_packet_inner<S: StateWrite>(
             .await?
             .unwrap_or_else(Amount::zero);
 
-        let new_value_balance = value_balance + value.amount;
+        let new_value_balance = value_balance.saturating_add(&value.amount);
         state.put(
             state_key::ics20_value_balance(&msg.packet.chan_on_b, &denom.id()),
             new_value_balance,
```
