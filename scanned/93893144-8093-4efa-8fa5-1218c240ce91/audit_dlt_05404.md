# [?] Merge #20372: Avoid signed integer overflow when loading a mempool.dat file with a malformed time field

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-11-12
Source: https://github.com/litecoin-project/litecoin/commit/027e51f715173d61c59514fd8deeea72f0c42ee8
Type: security-commit

## Details
Merge #20372: Avoid signed integer overflow when loading a mempool.dat file with a malformed time field

ee11a412a537f62aa46e8862678ce2069a2df5b7 Avoid signed integer overflow when loading a mempool.dat file with a malformed time field (practicalswift)

Pull request description:

  Avoid signed integer overflow when loading a `mempool.dat` file with a malformed time field.

  Avoid the following signed integer overflow:

  ```
  $ xxd -p -r > mempool.dat-crash-1 <<EOF
  0100000000000000000000000004000000000000000000000000ffffffff
  ffffff7f00000000000000000000000000
  EOF
  $ cp mempool.dat-crash-1 ~/.bitcoin/regtest/mempool.dat
  $ UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1:report_error_type=1" src/bitcoind -regtest
  validation.cpp:5079:23: runtime error: signed integer overflow: 9223372036854775807 + 1209600 cannot be represented in type 'long'
      #0 0x5618d335197f in LoadMempool(CTxMemPool&) src/validation.cpp:5079:23
      #1 0x5618d3350df3 in CChainState::LoadMempool(ArgsManager const&) src/validation.cpp:4217:9
      #2 0x5618d2b9345f in ThreadImport(ChainstateManager&, std::vector<boost::filesystem::path, std::allocator<boost::filesystem::path> >, ArgsManager const&) src/init.cpp:762:33
      #3 0x5618d2b92162 in AppInitMain(util::Ref const&, NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_14::operator()() const src/init.cpp:1881:9
  ```

  This PR was broken out from PR #20089. Hopefully this PR is trivial to review.

  Fixes a subset of #19278.

ACKs for top commit:
  MarcoFalke:
    review ACK ee11a412a537f62aa46e8862678ce2069a2df5b7
  Crypt-iQ:
    crACK ee11a412a537f62aa46e8862678ce2069a2df5b7

Tree-SHA512: 227ab95cd7d22f62f3191693b455eacfa8e36534961bee12c622fc9090957cfb29992eabafa74d806a336e03385aa8f98b7ce734f04b0b400e33aa187d353337
