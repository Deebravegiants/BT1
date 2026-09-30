# [?] Merge bitcoin/bitcoin#27271: RPC: Fix fund transaction crash when at 0-value, 0-fee

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-07-25
Source: https://github.com/dashpay/dash/commit/c07cb098b6265d9eefdc220c59de2405c8462b29
Type: security-commit

## Details
Merge bitcoin/bitcoin#27271: RPC: Fix fund transaction crash when at 0-value, 0-fee

Co-authored-by: Andrew Chow <github@achow101.com>
Co-authored-by: Claude Code <claude@anthropic.com>

## Patch
### src/wallet/spend.cpp
```diff
@@ -816,6 +816,13 @@ static std::optional<CreatedTransactionResult> CreateTransactionInternal(
     const CAmount not_input_fees = coin_selection_params.m_effective_feerate.GetFee(coin_selection_params.tx_noinputs_size);
     CAmount selection_target = recipients_sum + not_input_fees;
 
+    // This can only happen if feerate is 0, and requested destinations are value of 0 (e.g. OP_RETURN)
+    // and no pre-selected inputs. This will result in 0-input transaction, which is consensus-invalid anyways
+    if (selection_target == 0 && !coin_control.HasSelected()) {
+        error = _("Transaction requires one destination of non-0 value, a non-0 feerate, or a pre-selected input");
+        return std::nullopt;
+    }
+
     // Get available coins
     auto res_available_coins = AvailableCoins(wallet,
                                               &coin_control,
```

### test/functional/rpc_psbt.py
```diff
@@ -501,5 +501,8 @@ def test_psbt_input_keys(psbt_input, keys):
         assert signed['complete']
         self.nodes[0].finalizepsbt(signed['psbt'])
 
+        self.log.info("Test we don't crash when making a 0-value funded transaction at 0 fee without forcing an input selection")
+        assert_raises_rpc_error(-4, "Transaction requires one destination of non-0 value, a non-0 feerate, or a pre-selected input", self.nodes[0].walletcreatefundedpsbt, [], [{"data": "deadbeef"}], 0, {"fee_rate": "0"})
+
 if __name__ == '__main__':
     PSBTTest().main()
```
