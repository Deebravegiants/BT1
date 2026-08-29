# [?] Merge bitcoin/bitcoin#28969: fuzz: Avoid signed-integer-overflow in wallet_notifications fuzz target

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2023-11-29
Source: https://github.com/dashpay/dash/commit/f727f9bd94460949aa957d8867fbbcbb66a8e498
Type: security-commit

## Details
Merge bitcoin/bitcoin#28969: fuzz: Avoid signed-integer-overflow in wallet_notifications fuzz target

fab164f342ae089b3a8ccd33e6e3fd6de6e2217e fuzz: Avoid signed-integer-overflow in wallet_notifications fuzz target (MarcoFalke)

Pull request description:

  Should avoid

  ```
  policy/feerate.cpp:29:63: runtime error: signed integer overflow: 77600710321911316 * 149 cannot be represented in type 'int64_t' (aka 'long')
      #0 0x563a1775ed66 in CFeeRate::GetFee(unsigned int) const src/policy/feerate.cpp:29:63
      #1 0x563a15913a69 in wallet::COutput::COutput(COutPoint const&, CTxOut const&, int, int, bool, bool, bool, long, bool, std::optional<CFeeRate>) src/./wallet/coinselection.h:91:57
      #2 0x563a16fa6a6d in wallet::FetchSelectedInputs(wallet::CWallet const&, wallet::CCoinControl const&, wallet::CoinSelectionParams const&) src/wallet/spend.cpp:297:17
      #3 0x563a16fc4512 in wallet::CreateTransactionInternal(wallet::CWallet&, std::vector<wallet::CRecipient, std::allocator<wallet::CRecipient>> const&, int, wallet::CCoinControl const&, bool) src/wallet/spend.cpp:1105:33
      #4 0x563a16fbec74 in wallet::CreateTransaction(wallet::CWallet&, std::vector<wallet::CRecipient, std::allocator<wallet::CRecipient>> const&, int, wallet::CCoinControl const&, bool) src/wallet/spend.cpp:1291:16
      #5 0x563a16fcf6df in wallet::FundTransaction(wallet::CWallet&, CMutableTransaction&, long&, int&, bilingual_str&, bool, std::set<int, std::less<int>, std::allocator<int>> const&, wallet::CCoinControl) src/wallet/spend.cpp:1361:16
      #6 0x563a1597b7b9 in wallet::(anonymous namespace)::FuzzedWallet::FundTx(FuzzedDataProvider&, CMutableTransaction) src/wallet/test/fuzz/notifications.cpp:162:15
      #7 0x563a15958240 in wallet::(anonymous namespace)::wallet_notifications_fuzz_target(Span<unsigned char const>)::$_0::operator()() const src/wallet/test/fuzz/notifications.cpp:228:23
      #8 0x563a15958240 in unsigned long CallOneOf<wallet::(anonymous namespace)::wallet_notifications_fuzz_target(Span<unsigned char const>)::$_0, wallet::(anonymous namespace)::wallet_notifications_fuzz_target(Span<unsigned char const>)::$_1>(FuzzedDataProvider&, wallet::(anonymous namespace)::wallet_notifications_fuzz_target(Span<unsigned char const>)::$_0, wallet::(anonymous namespace)::wallet_notifications_fuzz_target(Span<unsigned char const>)::$_1) src/./test/fuzz/util.h:43:27
      #9 0x563a15958240 in wallet::(anonymous namespace)::wallet_notifications_fuzz_target(Span<unsigned char const>) src/wallet/test/fuzz/notifications.cpp:196:9
      #10 0x563a15fdef0c in std::function<void (Span<unsigned char const>)>::operator()(Span<unsigned char const>) const /usr/bin/../lib/gcc/x86_64-linux-gnu/13/../../../../include/c++/13/bits/std_function.h:591:9
      #11 0x563a15fdef0c in LLVMFuzzerTestOneInput src/test/fuzz/fuzz.cpp:178:5
      #12 0x563a158032a4 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long) (/ci_container_base/ci/scratch/build/bitcoin-x86_64-pc-linux-gnu/src/test/fuzz/fuzz+0x19822a4) (BuildId: 8acb42ad599d7f6d25b6f93e18fd564d80df7c06)
      #13 0x563a15802999 in fuzzer::Fuzzer::RunOne(unsigned char const*, unsigned long, bool, fuzzer::InputInfo*, bool, bool*) (/ci_container_base/ci/scratch/build/bitcoin-x86_64-pc-linux-gnu/src/test/fuzz/fuzz+0x1981999) (BuildId: 8acb42ad599d7f6d25b6f93e18fd564d80df7c06)
      #14 0x563a15804586 in fuzzer::Fuzzer::ReadAndExecuteSeedCorpora(std::vector<fuzzer::SizedFile, std::allocator<fuzzer::SizedFile>>&) (/ci_container_base/ci/scratch/build/bitcoin-x86_64-pc-linux-gnu/src/test/fuzz/fuzz+0x1983586) (BuildId: 8acb42ad599d7f6d25b6f93e18fd564d80df7c06)
      #15 0x563a15804aa7 in fuzzer::Fuzzer::Loop(std::vector<fuzzer::SizedFile, std::allocator<fuzzer::SizedFile>>&) (/ci_container_base/ci/scratch/build/bitcoin-x86_64-pc-linux-gnu/src/test/fuzz/fuzz+0x1983aa7) (BuildId: 8acb42ad599d7f6d25b6f93e18fd564d80df7c06)
      #16 0x563a157f21fb in fuzzer::FuzzerDriver(int*, char***, int (*)(unsigned char const*, unsigned long)) (/ci_container_base/ci/scratch/build/bitcoin-x86_64-pc-linux-gnu/src/test/fuzz/fuzz+0x19711fb) (BuildId: 8acb42ad599d7f6d25b6f93e18fd564d80df7c06)
      #17 0x563a1581c766 in main (/ci_container_base/ci/scratch/build/bitcoin-x86_64-pc-linux-gnu/src/test/fuzz/fuzz+0x199b766) (BuildId: 8acb42ad599d7f6d25b6f93e18fd564d80df7c06)
      #18 0x7f499e17b0cf  (/lib/x86_64-linux-gnu/libc.so.6+0x280cf) (BuildId: 96ab1a8f3b2c9a2ed37c7388615e6a726d037e89)
      #19 0x7f499e17b188 in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x28188) (BuildId: 96ab1a8f3b2c9a2ed37c7388615e6a726d037e89)
      #20 0x563a157e70c4 in _start (/ci_container_base/ci/scratch/build/bitcoin-x86_64-pc-linux-gnu/src/test/fuzz/fuzz+0x19660c4) (BuildId: 8acb42ad599d7f6d25b6f93e18fd564d80df7c06)

  SUMMARY: UndefinedBehaviorSanitizer: signed-integer-overflow policy/feerate.cpp:29:63 in
  MS: 0 ; base unit: 0000000000000000000000000000000000000000
  0x3f,0x0,0x2f,0x5f,0x5f,0x5f,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0x7d,0xff,0xff,0xff,0xff,0xff,0x53,0xff,0xff,0xff,0xff,0xff,0x0,0x0,0x0,0x0,0x0,0x0,0x13,0x5e,0x5f,0x5f,0x8,0x25,0x0,0x5f,0x5f,0x5f,0x5f,0x5f,0x5f,0x8,0x25,0xca,0x7f,0x5f,0x5f,0x5f,0x13,0x13,0x5f,0x5f,0x5f,0x2,0xdb,0xca,0x0,0x0,0xe7,0xe6,0x66,0x65,0x0,0x0,0x0,0x0,0x44,0x3f,0xa,0xa,0xff,0xff,0xff,0xff,0xff,0x61,0x76,0x6f,0x69,0x0,0xb5,0x15,
  ?\000/___}}}}}}}}}}}}}}}}}}}}\377\377\377\377\377S\377\377\377\377\377\000\000\000\000\000\000\023^__\010%\000______\010%\312\177___\023\023___\002\333\312\000\000\347\346fe\000\000\000\000D?\012\012\377\377\377\377\377avoi\000\265\025
  artifact_prefix='./'; Test unit written to ./crash-4d3bac8a64d4e58b2f0943e6d28e6e1f16328d7d
  Base64: PwAvX19ffX19fX19fX19fX19fX19fX19fX3//////1P//////wAAAAAAABNeX18IJQBfX19fX18IJcp/X19fExNfX18C28oAAOfmZmUAAAAARD8KCv//////YXZvaQC1FQ==
```

_Trimmed to 38 lines — full report: https://github.com/dashpay/dash/commit/f727f9bd94460949aa957d8867fbbcbb66a8e498_
