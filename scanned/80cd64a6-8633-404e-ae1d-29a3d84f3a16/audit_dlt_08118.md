# [?] simplewallet: fix crash in sweep commands when address is omitted

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2026-08-15
Source: https://github.com/monero-project/monero/commit/ddf0786ef7d36485b22f8682235187ab7a3585e3
Type: security-commit

## Details
simplewallet: fix crash in sweep commands when address is omitted

## Patch
### src/simplewallet/simplewallet.cpp
```diff
@@ -6975,6 +6975,13 @@ bool simple_wallet::sweep_main(uint32_t account, uint64_t below, const std::vect
       local_args.pop_back();
   }
 
+  if (local_args.empty())
+  {
+    fail_msg_writer() << tr("No address given");
+    print_usage();
+    return true;
+  }
+
   cryptonote::address_parse_info info;
   if (!cryptonote::get_account_address_from_str_or_url(info, m_wallet->nettype(), local_args[0], oa_prompter))
   {
```
