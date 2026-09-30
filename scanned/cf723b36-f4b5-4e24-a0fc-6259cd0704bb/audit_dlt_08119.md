# [?] simplewallet: fix potential out-of-bounds read

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2026-07-09
Source: https://github.com/monero-project/monero/commit/a9b891f4dbb9d3f8abc9b979a68f2a4214c89075
Type: security-commit

## Details
simplewallet: fix potential out-of-bounds read

## Patch
### src/simplewallet/simplewallet.cpp
```diff
@@ -203,7 +203,7 @@ namespace
   const char* USAGE_SWEEP_ACCOUNT("sweep_account <account> [index=<N1>[,<N2>,...] | index=all] [<priority>] [<ring_size>] [outputs=<N>] <address> [<payment_id (obsolete)>]");
   const char* USAGE_SWEEP_BELOW("sweep_below <amount_threshold> [index=<N1>[,<N2>,...]] [<priority>] [<ring_size>] <address> [<payment_id (obsolete)>]");
   const char* USAGE_SWEEP_SINGLE("sweep_single [<priority>] [<ring_size>] [outputs=<N>] <key_image> <address> [<payment_id (obsolete)>]");
-  const char* USAGE_DONATE("donate [index=<N1>[,<N2>,...]] [<priority>] [<ring_size>] <amount> [<payment_id (obsolete)>]");
+  const char* USAGE_DONATE("donate [index=<N1>[,<N2>,...]] [<priority>] [<ring_size>] <amount>");
   const char* USAGE_SIGN_TRANSFER("sign_transfer [export_raw] [<filename>]");
   const char* USAGE_SET_LOG("set_log <level>|{+,-,}<categories>");
   const char* USAGE_ACCOUNT("account\n"
@@ -7389,22 +7389,12 @@ bool simple_wallet::donate(const std::vector<std::string> &args_)
 {
   CHECK_IF_BACKGROUND_SYNCING("cannot donate");
   std::vector<std::string> local_args = args_;
-  if(local_args.empty() || local_args.size() > 5)
+  if(local_args.empty() || local_args.size() > 4)
   {
      PRINT_USAGE(USAGE_DONATE);
      return true;
   }
   std::string amount_str;
-  std::string payment_id_str;
-  // get payment id and pop
-  crypto::hash payment_id;
-  crypto::hash8 payment_id8;
-  if (tools::wallet2::parse_long_payment_id (local_args.back(), payment_id ) ||
-      tools::wallet2::parse_short_payment_id(local_args.back(), payment_id8))
-  {
-    payment_id_str = local_args.back();
-    local_args.pop_back();
-  }
   // get amount and pop
   uint64_t amount;
   bool ok = cryptonote::parse_amount(amount, local_args.back());
@@ -7418,7 +7408,7 @@ bool simple_wallet::donate(const std::vector<std::string> &args_)
     fail_msg_writer() << tr("amount is wrong: ") << local_args.back() << ", " << tr("expected number from 0 to ") << print_money(std::numeric_limits<uint64_t>::max());
     return true;
   }
-  // push back address, amount, payment id
+  // push back address, amount
   std::string address_str;
   if (m_wallet->nettype() != cryptonote::MAINNET)
   {
@@ -7437,8 +7427,6 @@ bool simple_wallet::donate(const std::vector<std::string> &args_)
   }
   local_args.push_back(address_str);
   local_args.push_back(amount_str);
-  if (!payment_id_str.empty())
-    local_args.push_back(payment_id_str);
   if (m_wallet->nettype() == cryptonote::MAINNET)
     message_writer() << (boost::format(tr("Donating %s %s to The Monero Project (donate.getmonero.org or %s).")) % amount_str % cryptonote::get_unit(cryptonote::get_default_decimal_point()) % MONERO_DONATION_ADDR).str();
   else
```
