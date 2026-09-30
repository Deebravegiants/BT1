# [?] Fix intermittent "fee" related crash in `rpc_blockchain.py`

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2023-03-24
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/e016eb31b1d68382f4c98997d747729fb3245761
Type: security-commit

## Details
Fix intermittent "fee" related crash in `rpc_blockchain.py`

This MR fixes an intermittent error with the rpc_blockchain functional test,
where the expected fee for transactions would not match the actual fee.
The original assertion expected the fee to always be equal to the
transaction size multiplied by the fee rate.
This is the ideal expected fee, but it will be wrong on occasion for two
reasons.
Firstly, the fees are determined by a worst-case estimate of the transaction
size (by CalculateMaximumSignedTxSize at wallet.cpp:3280).
The reason the transaction size estimate is occasionally overly conservative
is because the transaction values and fee need to be set before the transaction
can be signed.  It's only once the transaction is signed that the real size
materializes, by which time it is too late to correct the fee, hence the
discrepancy.
Secondly, fees are always rounded up to the nearest satoshi, which the
original assertion did not factor in.

Closes #469

# Changes

- Switched the assertion to use the assert_fee_amount function which was
  designed to handle such cases.
- Fleshed out documentation for ParseFixedPoint.  Based on the original
  function description, you would think that it would return a number
  equivalent to the string-encoded number being parsed.  But you would
  be off by a factor of 100,000,000 times in most cases!


# Test plan

- Convince yourself that

  while ./test/functional/test_runner.py rpc_blockchain; do sleep 0.1; done
  
  will not halt.
  Before the fix, this would take on average about 64 iteration to fail for me.

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
