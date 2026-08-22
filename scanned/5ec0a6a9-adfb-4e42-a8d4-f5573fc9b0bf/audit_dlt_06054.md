# [?] Merge bitcoin-core/gui#102: Fix SplashScreen crash when run with -disablewallet

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-10-13
Source: https://github.com/litecoin-project/litecoin/commit/ec0453cd57736df33e9f50c004d88bea10428ad5
Type: security-commit

## Details
Merge bitcoin-core/gui#102: Fix SplashScreen crash when run with -disablewallet

c056064a4a93be3601a63b37afea41f8b878df79 gui: Fix SplashScreen crash when run with -disablewallet (Hennadii Stepanov)

Pull request description:

  This PR fixes the bug introduced in https://github.com/bitcoin/bitcoin/pull/19099:

  ```
  $ src/qt/bitcoin-qt -disablewallet
  bitcoin-qt: interfaces/node.cpp:236: auto interfaces::(anonymous namespace)::NodeImpl::walletClient()::(anonymous class)::operator()() const: Assertion `"m_context->wallet_client" && check' failed.
  Aborted (core dumped)
  ```

ACKs for top commit:
  Sjors:
    tACK c056064
  promag:
    ACK c056064a4a93be3601a63b37afea41f8b878df79.

Tree-SHA512: 263d9efd5899cc6e447dfc5142bf911ca627149fac0a1c5e5b58dd196aa5e0d12fe13e3f750fb5f3c4338222f7959935d2f77391263f967dbca2e0e79a416a29
