# [?] wallet2: prevent crash when reading tx w/fewer outputs than expected

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2022-07-06
Source: https://github.com/monero-project/monero/commit/bd1e7c56356a7b282403bcff934360ae5523b848
Type: security-commit

## Details
wallet2: prevent crash when reading tx w/fewer outputs than expected

## Patch
### src/wallet/wallet2.h
```diff
@@ -349,6 +349,8 @@ namespace tools
       uint64_t amount() const { return m_amount; }
       const crypto::public_key get_public_key() const {
         crypto::public_key output_public_key;
+        THROW_WALLET_EXCEPTION_IF(m_tx.vout.size() <= m_internal_output_index,
+          error::wallet_internal_error, "Too few outputs, outputs may be corrupted");
         THROW_WALLET_EXCEPTION_IF(!get_output_public_key(m_tx.vout[m_internal_output_index], output_public_key),
           error::wallet_internal_error, "Unable to get output public key from output");
         return output_public_key;
```
