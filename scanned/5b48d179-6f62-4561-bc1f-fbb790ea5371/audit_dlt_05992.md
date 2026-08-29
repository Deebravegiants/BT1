# [?] Merge bitcoin/bitcoin#25077: Fix chain tip data race and corrupt rest response

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2022-08-17
Source: https://github.com/dashpay/dash/commit/7ab23ad795ea4a5fc0f9fb9adb7cdcdcbfde531f
Type: security-commit

## Details
Merge bitcoin/bitcoin#25077: Fix chain tip data race and corrupt rest response

fac04cb6ba1d032587bd02eab2247fd655a548cd refactor: Add lock annotations to Active* methods (MacroFake)
fac15ff673f0d6f84ea1eaae855597da02b0e510 Fix logical race in rest_getutxos (MacroFake)
fa97a528d6382a0163d5aa7d37ecbf93579b8186 Fix UB/data-race in RPCNotifyBlockChange (MacroFake)
fa530bcb9c13b58ab1b2068b48aa3fff910e2f87 Add ChainstateManager::GetMutex(), an alias for ::cs_main (MacroFake)

Pull request description:

  This fixes two issues:

  * A data race in `ActiveChain`, which returns a reference to the chain (a `std::vector`), which is not thread safe. See also below traceback.
  * A corrupt rest response, which returns a blockheight and blockhash, which are unrelated to each other and to the result, as the chain might advance between each call without cs_main held.

  The issues are fixed by taking cs_main and holding it for the required time.

  ```
  ==================
  WARNING: ThreadSanitizer: data race (pid=32335)
    Write of size 8 at 0x7b3c000008f0 by thread T22 (mutexes: write M131626, write M151, write M131553):
      #0 std::__1::enable_if<(is_move_constructible<CBlockIndex**>::value) && (is_move_assignable<CBlockIndex**>::value), void>::type std::__1::swap<CBlockIndex**>(CBlockIndex**&, CBlockIndex**&) /usr/lib/llvm-13/bin/../include/c++/v1/__utility/swap.h:39:7 (bitcoind+0x501239)
      #1 std::__1::vector<CBlockIndex*, std::__1::allocator<CBlockIndex*> >::__swap_out_circular_buffer(std::__1::__split_buffer<CBlockIndex*, std::__1::allocator<CBlockIndex*>&>&) /usr/lib/llvm-13/bin/../include/c++/v1/vector:977:5 (bitcoind+0x501239)
      #2 std::__1::vector<CBlockIndex*, std::__1::allocator<CBlockIndex*> >::__append(unsigned long) /usr/lib/llvm-13/bin/../include/c++/v1/vector:1117:9 (bitcoind+0x501239)
      #3 std::__1::vector<CBlockIndex*, std::__1::allocator<CBlockIndex*> >::resize(unsigned long) /usr/lib/llvm-13/bin/../include/c++/v1/vector:2046:15 (bitcoind+0x4ffe29)
      #4 CChain::SetTip(CBlockIndex*) src/chain.cpp:19:12 (bitcoind+0x4ffe29)
      #5 CChainState::ConnectTip(BlockValidationState&, CBlockIndex*, std::__1::shared_ptr<CBlock const> const&, ConnectTrace&, DisconnectedBlockTransactions&) src/validation.cpp:2748:13 (bitcoind+0x475d00)
      #6 CChainState::ActivateBestChainStep(BlockValidationState&, CBlockIndex*, std::__1::shared_ptr<CBlock const> const&, bool&, ConnectTrace&) src/validation.cpp:2884:18 (bitcoind+0x47739e)
      #7 CChainState::ActivateBestChain(BlockValidationState&, std::__1::shared_ptr<CBlock const>) src/validation.cpp:3011:22 (bitcoind+0x477baf)
      #8 node::ThreadImport(ChainstateManager&, std::__1::vector<fs::path, std::__1::allocator<fs::path> >, ArgsManager const&) src/node/blockstorage.cpp:883:30 (bitcoind+0x23cd74)
      #9 AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7::operator()() const src/init.cpp:1657:9 (bitcoind+0x15863e)
      #10 decltype(static_cast<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&>(fp)()) std::__1::__invoke<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&>(AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&) /usr/lib/llvm-13/bin/../include/c++/v1/type_traits:3918:1 (bitcoind+0x15863e)
      #11 void std::__1::__invoke_void_return_wrapper<void, true>::__call<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&>(AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&) /usr/lib/llvm-13/bin/../include/c++/v1/__functional/invoke.h:61:9 (bitcoind+0x15863e)
      #12 std::__1::__function::__alloc_func<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7, std::__1::allocator<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>, void ()>::operator()() /usr/lib/llvm-13/bin/../include/c++/v1/__functional/function.h:171:16 (bitcoind+0x15863e)
      #13 std::__1::__function::__func<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7, std::__1::allocator<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>, void ()>::operator()() /usr/lib/llvm-13/bin/../include/c++/v1/__functional/function.h:345:12 (bitcoind+0x15863e)
      #14 std::__1::__function::__value_func<void ()>::operator()() const /usr/lib/llvm-13/bin/../include/c++/v1/__functional/function.h:498:16 (bitcoind+0x88891f)
      #15 std::__1::function<void ()>::operator()() const /usr/lib/llvm-13/bin/../include/c++/v1/__functional/function.h:1175:12 (bitcoind+0x88891f)
      #16 util::TraceThread(char const*, std::__1::function<void ()>) src/util/thread.cpp:18:9 (bitcoind+0x88891f)
      #17 decltype(static_cast<void (*>(fp)(static_cast<char const*>(fp0), static_cast<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>(fp0))) std::__1::__invoke<void (*)(char const*, std::__1::function<void ()>), char const*, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>(void (*&&)(char const*, std::__1::function<void ()>), char const*&&, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&&) /usr/lib/llvm-13/bin/../include/c++/v1/type_traits:3918:1 (bitcoind+0x157e6a)
```

_Trimmed to 38 lines — full report: https://github.com/dashpay/dash/commit/7ab23ad795ea4a5fc0f9fb9adb7cdcdcbfde531f_
