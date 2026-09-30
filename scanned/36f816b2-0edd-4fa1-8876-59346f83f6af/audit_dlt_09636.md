# [?] merge bitcoin#25213: fix crash at coinselection, add missing fee rate

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2022-05-25
Source: https://github.com/dashpay/dash/commit/0b915e7d512b1787f8145d9fc89bea7e2690dc42
Type: security-commit

## Details
merge bitcoin#25213: fix crash at coinselection, add missing fee rate

## Patch
### src/wallet/test/fuzz/coinselection.cpp
```diff
@@ -15,13 +15,13 @@
 
 namespace wallet {
 
-static void AddCoin(const CAmount& value, int n_input, int n_input_bytes, int locktime, std::vector<COutput>& coins)
+static void AddCoin(const CAmount& value, int n_input, int n_input_bytes, int locktime, std::vector<COutput>& coins, CFeeRate fee_rate)
 {
     CMutableTransaction tx;
     tx.vout.resize(n_input + 1);
     tx.vout[n_input].nValue = value;
     tx.nLockTime = locktime; // all transactions get different hashes
-    coins.emplace_back(COutPoint(tx.GetHash(), n_input), tx.vout.at(n_input), /*depth=*/0, n_input_bytes, /*spendable=*/true, /*solvable=*/true, /*safe=*/true, /*time=*/0, /*from_me=*/true);
+    coins.emplace_back(COutPoint(tx.GetHash(), n_input), tx.vout.at(n_input), /*depth=*/0, n_input_bytes, /*spendable=*/true, /*solvable=*/true, /*safe=*/true, /*time=*/0, /*from_me=*/true, fee_rate);
 }
 
 // Randomly distribute coins to instances of OutputGroup
@@ -71,7 +71,7 @@ FUZZ_TARGET(coinselection)
         if (total_balance + amount >= MAX_MONEY) {
             break;
         }
-        AddCoin(amount, n_input, n_input_bytes, ++next_locktime, utxo_pool);
+        AddCoin(amount, n_input, n_input_bytes, ++next_locktime, utxo_pool, coin_params.m_effective_feerate);
         total_balance += amount;
     }
 
```
