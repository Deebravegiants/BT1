# [?] Merge bitcoin/bitcoin#29434: rpc: Fixed signed integer overflow for large feerates

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2024-02-19
Source: https://github.com/dashpay/dash/commit/ed95384919fa9187bf0c7b66aefe8efc5cfd164c
Type: security-commit

## Details
Merge bitcoin/bitcoin#29434: rpc: Fixed signed integer overflow for large feerates

dddd7be9bf038c25f3e53c5bd708fb9cf73d4493 doc: Clarify maxfeerate help (MarcoFalke)
fa2a4fdef779b01e847def5985deafedc6dd3da8 rpc: Fixed signed integer overflow for large feerates (MarcoFalke)
fade94d11a5b93113975c4b2f62a357a70d03191 rpc: Add ParseFeeRate helper (MarcoFalke)
fa0ff6610944fdda716fb0134b78cb85a4c9c26d rpc: Implement RPCHelpMan::ArgValue<> for UniValue (MarcoFalke)

Pull request description:

  Passing large BTC/kvB feerates to RPCs is problematic, because:

  * They are likely a typo. 1BTC/kvB (or larger) seems absurd.
  * They may cause signed integer overflow.
  * Anyone really wanting to pick such a large value can set `0` to disable the check.

  Fix all issues by rejecting anything more than 1BTC/kvB during parsing.

ACKs for top commit:
  brunoerg:
    crACK dddd7be9bf038c25f3e53c5bd708fb9cf73d4493
  achow101:
    ACK dddd7be9bf038c25f3e53c5bd708fb9cf73d4493
  vasild:
    ACK dddd7be9bf038c25f3e53c5bd708fb9cf73d4493
  tdb3:
    Code review ACK and basic test ACK for dddd7be9bf038c25f3e53c5bd708fb9cf73d4493.
  fjahr:
    utACK dddd7be9bf038c25f3e53c5bd708fb9cf73d4493

Tree-SHA512: 5dcce1f0abe059dc6b2ff56787e11081d73a45b4ddd6dcc2c1ea13709ebc13af5e7265e84fffb97ef32027b56b81955672a67ed7702e8fa30c2e849d67727bac

## Patch
### src/rpc/mempool.cpp
```diff
@@ -46,7 +46,7 @@ RPCHelpMan sendrawtransaction()
             {"hexstring", RPCArg::Type::STR_HEX, RPCArg::Optional::NO, "The hex string of the raw transaction"},
             {"maxfeerate", RPCArg::Type::AMOUNT, RPCArg::Default{FormatMoney(DEFAULT_MAX_RAW_TX_FEE_RATE.GetFeePerK())},
              "Reject transactions whose fee rate is higher than the specified value, expressed in " + CURRENCY_UNIT +
-                 "/kB.\nSet to 0 to accept any fee rate.\n"},
+                 "/kB.\nFee rates larger than 1" + CURRENCY_UNIT + "/kB are rejected.\nSet to 0 to accept any fee rate.\n"},
             {"instantsend", RPCArg::Type::BOOL, RPCArg::Optional::OMITTED, "Deprecated and ignored"},
             {"bypasslimits", RPCArg::Type::BOOL, RPCArg::Default{false}, "Bypass transaction policy limits"},
         },
@@ -78,9 +78,7 @@ RPCHelpMan sendrawtransaction()
             }
             CTransactionRef tx(MakeTransactionRef(std::move(mtx)));
 
-            const CFeeRate max_raw_tx_fee_rate = request.params[1].isNull() ?
-                                                     DEFAULT_MAX_RAW_TX_FEE_RATE :
-                                                     CFeeRate(AmountFromValue(request.params[1]));
+            const CFeeRate max_raw_tx_fee_rate{ParseFeeRate(self.Arg<UniValue>(1))};
 
             int64_t virtual_size = GetVirtualTransactionSize(*tx);
             CAmount max_raw_tx_fee = max_raw_tx_fee_rate.GetFee(virtual_size);
@@ -116,7 +114,8 @@ static RPCHelpMan testmempoolaccept()
                 },
             },
             {"maxfeerate", RPCArg::Type::AMOUNT, RPCArg::Default{FormatMoney(DEFAULT_MAX_RAW_TX_FEE_RATE.GetFeePerK())},
-             "Reject transactions whose fee rate is higher than the specified value, expressed in " + CURRENCY_UNIT + "/kB\n"},
+             "Reject transactions whose fee rate is higher than the specified value, expressed in " + CURRENCY_UNIT +
+                 "/kB\nFee rates larger than 1" + CURRENCY_UNIT + "/kB are rejected.\nSet to 0 to accept any fee rate."},
         },
         RPCResult{
             RPCResult::Type::ARR, "", "The result of the mempool acceptance test for each raw transaction in the input array.\n"
@@ -160,9 +159,7 @@ static RPCHelpMan testmempoolaccept()
                                    "Array must contain between 1 and " + ToString(MAX_PACKAGE_COUNT) + " transactions.");
             }
 
-            const CFeeRate max_raw_tx_fee_rate = request.params[1].isNull() ?
-                                                     DEFAULT_MAX_RAW_TX_FEE_RATE :
-                                                     CFeeRate(AmountFromValue(request.params[1]));
+            const CFeeRate max_raw_tx_fee_rate{ParseFeeRate(self.Arg<UniValue>(1))};
 
             std::vector<CTransactionRef> txns;
             txns.reserve(raw_transactions.size());
```

### src/rpc/util.cpp
```diff
@@ -95,6 +95,13 @@ CAmount AmountFromValue(const UniValue& value, int decimals)
     return amount;
 }
 
+CFeeRate ParseFeeRate(const UniValue& json)
+{
+    CAmount val{AmountFromValue(json)};
+    if (val >= COIN) throw JSONRPCError(RPC_INVALID_PARAMETER, "Fee rates larger than or equal to 1" + CURRENCY_UNIT + "/kB are not accepted");
+    return CFeeRate{val};
+}
+
 uint256 ParseHashV(const UniValue& v, std::string strName)
 {
     const std::string& strHex(v.get_str());
@@ -569,11 +576,13 @@ static void CheckRequiredOrDefault(const RPCArg& param)
     void force_semicolon(ret_type)
 
 // Optional arg (without default). Can also be called on required args, if needed.
+TMPL_INST(nullptr, const UniValue*, maybe_arg;);
 TMPL_INST(nullptr, std::optional<double>, maybe_arg ? std::optional{maybe_arg->get_real()} : std::nullopt;);
 TMPL_INST(nullptr, std::optional<bool>, maybe_arg ? std::optional{maybe_arg->get_bool()} : std::nullopt;);
 TMPL_INST(nullptr, const std::string*, maybe_arg ? &maybe_arg->get_str() : nullptr;);
 
 // Required arg or optional arg with default value.
+TMPL_INST(CheckRequiredOrDefault, const UniValue&, *CHECK_NONFATAL(maybe_arg););
 TMPL_INST(CheckRequiredOrDefault, int, CHECK_NONFATAL(maybe_arg)->getInt<int>(););
 TMPL_INST(CheckRequiredOrDefault, uint64_t, CHECK_NONFATAL(maybe_arg)->getInt<uint64_t>(););
 TMPL_INST(CheckRequiredOrDefault, const std::string&, CHECK_NONFATAL(maybe_arg)->get_str(););
```

### src/rpc/util.h
```diff
@@ -118,6 +118,11 @@ bool ParseBoolV(const UniValue& v, const std::string &strName);
  * @returns a CAmount if the various checks pass.
  */
 CAmount AmountFromValue(const UniValue& value, int decimals = 8);
+/**
+ * Parse a json number or string, denoting BTC/kvB, into a CFeeRate (sat/kvB).
+ * Reject negative values or rates larger than 1DASH/kB.
+ */
+CFeeRate ParseFeeRate(const UniValue& json);
 
 using RPCArgList = std::vector<std::pair<std::string, UniValue>>;
 std::string HelpExampleCli(const std::string& methodname, const std::string& args);
```

### test/functional/mempool_accept.py
```diff
@@ -82,9 +82,17 @@ def run_test(self):
             rawtxs=[raw_tx_in_block],
             maxfeerate=-0.01,
         ))
+        # Also check feerate. 1DASH/kB fails
+        assert_raises_rpc_error(-8, "Fee rates larger than or equal to 1DASH/kB are not accepted", lambda: self.check_mempool_result(
+            result_expected=None,
+            rawtxs=[raw_tx_in_block],
+            maxfeerate=1,
+        ))
+        # ... 0.99 passes
         self.check_mempool_result(
             result_expected=[{'txid': txid_in_block, 'allowed': False, 'reject-reason': 'txn-already-known'}],
             rawtxs=[raw_tx_in_block],
+            maxfeerate=0.99,
         )
 
         self.log.info('A transaction not in the mempool')
```
