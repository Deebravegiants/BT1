# [?] Merge branch 'fix-intermittent-fee-crash' into 'master'

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2023-03-24
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/37073d4ae0d40c0524e910e4436d76311e3029b5
Type: security-commit

## Details
Merge branch 'fix-intermittent-fee-crash' into 'master'

Fix intermittent "fee" related crash in `rpc_blockchain.py`

Closes #469

See merge request bitcoin-cash-node/bitcoin-cash-node!1721

## Patch
### src/util/strencodings.h
```diff
@@ -228,9 +228,11 @@ template <typename T> bool TimingResistantEqual(const T &a, const T &b) {
 /**
  * Parse number as fixed point according to JSON number syntax.
  * See http://json.org/number.gif
- * @returns true on success, false on error.
- * @note The result must be in the range (-10^18,10^18), otherwise an overflow
- * error will trigger.
+ * @returns     true on success, false on error.
+ * @param[in]   val A string representation of a number to be parsed.
+ * @param[in]   decimals The number of decimal places from \p val to be considered.
+ * @param[out]  amount_out The parsed integer number, equivalent to \p val multiplied by \p decimal.
+ * @note        The result must be in the range (-10^18,10^18), otherwise an overflow error will trigger.
  */
 [[nodiscard]] bool ParseFixedPoint(const std::string &val, int decimals, int64_t *amount_out);
 
```

### test/functional/rpc_blockchain.py
```diff
@@ -30,6 +30,7 @@
 from test_framework.test_framework import BitcoinTestFramework, get_datadir_path
 from test_framework.util import (
     assert_equal,
+    assert_fee_amount,
     assert_greater_than,
     assert_greater_than_or_equal,
     assert_raises,
@@ -458,7 +459,7 @@ def assert_fee_in_block(verbosity):
             block = node.getblock(blockhash, verbosity)
             tx = block['tx'][1]
             assert 'fee' in tx
-            assert_equal(tx['fee'] * COIN, tx['size'] * fee_per_byte)
+            assert_fee_amount(tx['fee'], tx['size'], fee_per_byte * 1000 / COIN)
 
         def assert_vin_contains_prevout(verbosity):
             block = node.getblock(blockhash, verbosity)
```
