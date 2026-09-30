# [?] fix: overflow check hardening

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-09-09
Source: https://github.com/fedimint/fedimint/commit/bb86342d7e6432fe3190e56a34805eb13f2963da
Type: security-commit

## Details
fix: overflow check hardening

## Patch
### fedimint-core/src/amount.rs
```diff
@@ -50,6 +50,14 @@ uniffi::custom_type!(Amount, u64, {
 impl Amount {
     pub const ZERO: Self = Self { msats: 0 };
 
+    /// The largest amount that can ever exist, in millisatoshis: the
+    /// 21,000,000 BTC supply cap. No valid payment can exceed this, so callers
+    /// that accept externally-supplied amounts should reject anything larger to
+    /// keep subsequent fee and total arithmetic from overflowing `u64`.
+    pub const MAX_BITCOIN_SUPPLY: Self = Self {
+        msats: 21_000_000 * SATS_PER_BITCOIN * 1000,
+    };
+
     /// Create an amount from a number of millisatoshis.
     pub const fn from_msats(msats: u64) -> Self {
         Self { msats }
```

### modules/fedimint-gw-client/src/pay.rs
```diff
@@ -163,6 +163,8 @@ pub enum OutgoingContractError {
     MissingContractData,
     #[error("The invoice is expired. Expiry happened at timestamp: {0}")]
     InvoiceExpired(u64),
+    #[error("The invoice amount exceeds the total bitcoin supply")]
+    InvoiceAmountTooLarge,
 }
 
 #[derive(
@@ -649,8 +651,18 @@ impl GatewayPayInvoice {
             .amount()
             .ok_or(OutgoingContractError::InvoiceMissingAmount)?;
 
+        // A pruned invoice carries a raw, caller-controlled amount. Reject
+        // anything above the bitcoin supply cap, and add the fee with checked
+        // arithmetic, so a huge amount cannot overflow `u64` and wrap the
+        // underfunding check below into passing against a near-empty contract.
+        if payment_amount > Amount::MAX_BITCOIN_SUPPLY {
+            return Err(OutgoingContractError::InvoiceAmountTooLarge);
+        }
+
         let gateway_fee = routing_fees.to_amount(&payment_amount);
-        let necessary_contract_amount = payment_amount + gateway_fee;
+        let necessary_contract_amount = payment_amount
+            .checked_add(gateway_fee)
+            .ok_or(OutgoingContractError::InvoiceAmountTooLarge)?;
         if account.amount < necessary_contract_amount {
             return Err(OutgoingContractError::Underfunded(
                 necessary_contract_amount,
@@ -1023,11 +1035,19 @@ mod tests {
     fn contract_account_with_timelock(
         hash: sha256::Hash,
         timelock: u32,
+    ) -> OutgoingContractAccount {
+        contract_account_with(hash, INVOICE_AMOUNT, timelock)
+    }
+
+    fn contract_account_with(
+        hash: sha256::Hash,
+        amount: Amount,
+        timelock: u32,
     ) -> OutgoingContractAccount {
         let gateway_key = secp256k1::PublicKey::from_keypair(&gateway_keypair());
 
         OutgoingContractAccount {
-            amount: INVOICE_AMOUNT,
+            amount,
             contract: OutgoingContract {
                 hash,
                 gateway_key,
@@ -1039,8 +1059,12 @@ mod tests {
     }
 
     fn payment_data(payment_hash: sha256::Hash) -> PaymentData {
+        pruned_payment_data(payment_hash, INVOICE_AMOUNT)
+    }
+
+    fn pruned_payment_data(payment_hash: sha256::Hash, amount: Amount) -> PaymentData {
         PaymentData::PrunedInvoice(PrunedInvoice {
-            amount: INVOICE_AMOUNT,
+            amount,
             destination: secp256k1::PublicKey::from_keypair(&gateway_keypair()),
             destination_features: vec![],
             payment_hash,
@@ -1129,4 +1153,47 @@ mod tests {
             })
         );
     }
+
+    /// A pruned invoice's amount is a raw, caller-supplied `u64`. An amount so
+    /// large that `payment_amount + fee` overflows must be rejected: otherwise
+    /// the sum wraps to a small value, the underfunding check passes against a
+    /// near-empty contract, and the gateway pays out real funds it can never
+    /// reclaim.
+    #[test]
+    fn rejects_invoice_amount_that_would_overflow_the_underfunding_check() {
+        let hash = sha256::Hash::hash(b"preimage");
+
+        // A one-millisatoshi base fee makes `u64::MAX + fee` wrap to zero, so
+        // before the fix the underfunding check passed against any contract.
+        let fees = RoutingFees {
+            base_msat: 1,
+            proportional_millionths: 0,
+        };
+
+        let validate_amount = |contract_amount: Amount, invoice_amount: Amount| {
+            GatewayPayInvoice::validate_outgoing_account(
+                &contract_account_with(hash, contract_amount, 100),
+                gateway_keypair(),
+                CONSENSUS_BLOCK_COUNT,
+                &pruned_payment_data(hash, invoice_amount),
+                fees,
+            )
+            .map(|_| ())
+        };
+
+        // The attack: a wrapping invoice amount against a near-empty contract.
+        assert_eq!(
+            validate_amount(Amount::from_msats(1), Amount::from_msats(u64::MAX)),
+            Err(OutgoingContractError::InvoiceAmountTooLarge)
+        );
+
+        // The supply cap itself is a legitimate amount and is still accepted
+        // when the contract funds it plus the fee, so the guard rejects only
+        // genuinely invalid sizes rather than everything.
+        let cap = Amount::MAX_BITCOIN_SUPPLY;
+        let funded = cap
+            .checked_add(Amount::from_msats(u64::from(fees.base_msat)))
+            .expect("cap plus a tiny fee stays within u64");
+        assert_eq!(validate_amount(funded, cap), Ok(()));
+    }
 }
```
