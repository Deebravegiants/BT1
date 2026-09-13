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
      #18 void std::__1::__thread_execute<std::__1::unique_ptr<std::__1::__thread_struct, std::__1::default_delete<std::__1::__thread_struct> >, void (*)(char const*, std::__1::function<void ()>), char const*, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7, 2ul, 3ul>(std::__1::tuple<std::__1::unique_ptr<std::__1::__thread_struct, std::__1::default_delete<std::__1::__thread_struct> >, void (*)(char const*, std::__1::function<void ()>), char const*, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>&, std::__1::__tuple_indices<2ul, 3ul>) /usr/lib/llvm-13/bin/../include/c++/v1/thread:280:5 (bitcoind+0x157e6a)
      #19 void* std::__1::__thread_proxy<std::__1::tuple<std::__1::unique_ptr<std::__1::__thread_struct, std::__1::default_delete<std::__1::__thread_struct> >, void (*)(char const*, std::__1::function<void ()>), char const*, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7> >(void*) /usr/lib/llvm-13/bin/../include/c++/v1/thread:291:5 (bitcoind+0x157e6a)
    Previous read of size 8 at 0x7b3c000008f0 by main thread:
      #0 std::__1::vector<CBlockIndex*, std::__1::allocator<CBlockIndex*> >::size() const /usr/lib/llvm-13/bin/../include/c++/v1/vector:680:61 (bitcoind+0x15179d)
      #1 CChain::Tip() const src/./chain.h:449:23 (bitcoind+0x15179d)
      #2 ChainstateManager::ActiveTip() const src/./validation.h:927:59 (bitcoind+0x15179d)
      #3 AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*) src/init.cpp:1841:35 (bitcoind+0x15179d)
      #4 AppInit(node::NodeContext&, int, char**) src/bitcoind.cpp:231:43 (bitcoind+0x133fd2)
      #5 main src/bitcoind.cpp:275:13 (bitcoind+0x133fd2)
    Location is heap block of size 232 at 0x7b3c00000870 allocated by main thread:
      #0 operator new(unsigned long) <null> (bitcoind+0x132668)
      #1 ChainstateManager::InitializeChainstate(CTxMemPool*, std::__1::optional<uint256> const&) src/validation.cpp:4851:21 (bitcoind+0x48e26b)
      #2 node::LoadChainstate(bool, ChainstateManager&, CTxMemPool*, bool, Consensus::Params const&, bool, long, long, long, bool, bool, std::__1::function<bool ()>, std::__1::function<void ()>) src/node/chainstate.cpp:31:14 (bitcoind+0x24de07)
      #3 AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*) src/init.cpp:1438:32 (bitcoind+0x14e994)
      #4 AppInit(node::NodeContext&, int, char**) src/bitcoind.cpp:231:43 (bitcoind+0x133fd2)
      #5 main src/bitcoind.cpp:275:13 (bitcoind+0x133fd2)
    Mutex M131626 (0x7b3c00000898) created at:
      #0 pthread_mutex_lock <null> (bitcoind+0xda898)
      #1 std::__1::mutex::lock() <null> (libc++.so.1+0x49f35)
      #2 node::ThreadImport(ChainstateManager&, std::__1::vector<fs::path, std::__1::allocator<fs::path> >, ArgsManager const&) src/node/blockstorage.cpp:883:30 (bitcoind+0x23cd74)
      #3 AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7::operator()() const src/init.cpp:1657:9 (bitcoind+0x15863e)
      #4 decltype(static_cast<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&>(fp)()) std::__1::__invoke<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&>(AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&) /usr/lib/llvm-13/bin/../include/c++/v1/type_traits:3918:1 (bitcoind+0x15863e)
      #5 void std::__1::__invoke_void_return_wrapper<void, true>::__call<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&>(AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&) /usr/lib/llvm-13/bin/../include/c++/v1/__functional/invoke.h:61:9 (bitcoind+0x15863e)
      #6 std::__1::__function::__alloc_func<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7, std::__1::allocator<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>, void ()>::operator()() /usr/lib/llvm-13/bin/../include/c++/v1/__functional/function.h:171:16 (bitcoind+0x15863e)
      #7 std::__1::__function::__func<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7, std::__1::allocator<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>, void ()>::operator()() /usr/lib/llvm-13/bin/../include/c++/v1/__functional/function.h:345:12 (bitcoind+0x15863e)
      #8 std::__1::__function::__value_func<void ()>::operator()() const /usr/lib/llvm-13/bin/../include/c++/v1/__functional/function.h:498:16 (bitcoind+0x88891f)
      #9 std::__1::function<void ()>::operator()() const /usr/lib/llvm-13/bin/../include/c++/v1/__functional/function.h:1175:12 (bitcoind+0x88891f)
      #10 util::TraceThread(char const*, std::__1::function<void ()>) src/util/thread.cpp:18:9 (bitcoind+0x88891f)
      #11 decltype(static_cast<void (*>(fp)(static_cast<char const*>(fp0), static_cast<AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>(fp0))) std::__1::__invoke<void (*)(char const*, std::__1::function<void ()>), char const*, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>(void (*&&)(char const*, std::__1::function<void ()>), char const*&&, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&&) /usr/lib/llvm-13/bin/../include/c++/v1/type_traits:3918:1 (bitcoind+0x157e6a)
      #12 void std::__1::__thread_execute<std::__1::unique_ptr<std::__1::__thread_struct, std::__1::default_delete<std::__1::__thread_struct> >, void (*)(char const*, std::__1::function<void ()>), char const*, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7, 2ul, 3ul>(std::__1::tuple<std::__1::unique_ptr<std::__1::__thread_struct, std::__1::default_delete<std::__1::__thread_struct> >, void (*)(char const*, std::__1::function<void ()>), char const*, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7>&, std::__1::__tuple_indices<2ul, 3ul>) /usr/lib/llvm-13/bin/../include/c++/v1/thread:280:5 (bitcoind+0x157e6a)
      #13 void* std::__1::__thread_proxy<std::__1::tuple<std::__1::unique_ptr<std::__1::__thread_struct, std::__1::default_delete<std::__1::__thread_struct> >, void (*)(char const*, std::__1::function<void ()>), char const*, AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7> >(void*) /usr/lib/llvm-13/bin/../include/c++/v1/thread:291:5 (bitcoind+0x157e6a)
    Mutex M151 (0x55aacb8ea030) created at:
      #0 pthread_mutex_init <null> (bitcoind+0xbed2f)
      #1 std::__1::recursive_mutex::recursive_mutex() <null> (libc++.so.1+0x49fb3)
      #2 __libc_start_main <null> (libc.so.6+0x29eba)
    Mutex M131553 (0x7b4c000042e0) created at:
      #0 pthread_mutex_init <null> (bitcoind+0xbed2f)
      #1 std::__1::recursive_mutex::recursive_mutex() <null> (libc++.so.1+0x49fb3)
      #2 std::__1::__unique_if<CTxMemPool>::__unique_single std::__1::make_unique<CTxMemPool, CBlockPolicyEstimator*, int const&>(CBlockPolicyEstimator*&&, int const&) /usr/lib/llvm-13/bin/../include/c++/v1/__memory/unique_ptr.h:728:32 (bitcoind+0x15c81d)
      #3 AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*) src/init.cpp:1426:24 (bitcoind+0x14e7b4)
      #4 AppInit(node::NodeContext&, int, char**) src/bitcoind.cpp:231:43 (bitcoind+0x133fd2)
      #5 main src/bitcoind.cpp:275:13 (bitcoind+0x133fd2)
    Thread T22 'b-loadblk' (tid=32370, running) created by main thread at:
      #0 pthread_create <null> (bitcoind+0xbd5bd)
      #1 std::__1::__libcpp_thread_create(unsigned long*, void* (*)(void*), void*) /usr/lib/llvm-13/bin/../include/c++/v1/__threading_support:443:10 (bitcoind+0x155e06)
      #2 std::__1::thread::thread<void (*)(char const*, std::__1::function<void ()>), char const (&) [8], AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7, void>(void (*&&)(char const*, std::__1::function<void ()>), char const (&) [8], AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*)::$_7&&) /usr/lib/llvm-13/bin/../include/c++/v1/thread:307:16 (bitcoind+0x155e06)
      #3 AppInitMain(node::NodeContext&, interfaces::BlockAndHeaderTipInfo*) src/init.cpp:1656:29 (bitcoind+0x150164)
      #4 AppInit(node::NodeContext&, int, char**) src/bitcoind.cpp:231:43 (bitcoind+0x133fd2)
      #5 main src/bitcoind.cpp:275:13 (bitcoind+0x133fd2)
  SUMMARY: ThreadSanitizer: data race /usr/lib/llvm-13/bin/../include/c++/v1/__utility/swap.h:39:7 in std::__1::enable_if<(is_move_constructible<CBlockIndex**>::value) && (is_move_assignable<CBlockIndex**>::value), void>::type std::__1::swap<CBlockIndex**>(CBlockIndex**&, CBlockIndex**&)
  ==================
  ```

  From https://cirrus-ci.com/task/5612886578954240?logs=ci#L4868

ACKs for top commit:
  achow101:
    re-ACK fac04cb6ba1d032587bd02eab2247fd655a548cd
  theStack:
    Code-review ACK fac04cb6ba1d032587bd02eab2247fd655a548cd

Tree-SHA512: 9d619f99ff6373874c7ffe1db20674575605646b4b54b692fb54515a4a49f110a770026d7320ed6dfeaa7976be4cd89e93f821acdbf22c7662bd1c5be0cedcd2

### src/bitcoin-chainstate.cpp
```diff
@@ -153,12 +153,14 @@ int main(int argc, char* argv[])
     // Main program logic starts here
     std::cout
         << "Hello! I'm going to print out some information about your datadir." << std::endl
-        << "\t" << "Path: " << gArgs.GetDataDirNet() << std::endl
+        << "\t" << "Path: " << gArgs.GetDataDirNet() << std::endl;
+    {
+        LOCK(chainman.GetMutex());
+        std::cout
         << "\t" << "Reindexing: " << std::boolalpha << node::fReindex.load() << std::noboolalpha << std::endl
         << "\t" << "Snapshot Active: " << std::boolalpha << chainman.IsSnapshotActive() << std::noboolalpha << std::endl
         << "\t" << "Active Height: " << chainman.ActiveHeight() << std::endl
         << "\t" << "Active IBD: " << std::boolalpha << chainman.ActiveChainstate().IsInitialBlockDownload() << std::noboolalpha << std::endl;
-    {
         CBlockIndex* tip = chainman.ActiveTip();
         if (tip) {
             std::cout << "\t" << tip->ToString() << std::endl;
```

### src/init.cpp
```diff
@@ -2470,7 +2470,7 @@ bool AppInitMain(NodeContext& node, interfaces::BlockAndHeaderTipInfo* tip_info)
     // Either install a handler to notify us when genesis activates, or set fHaveGenesis directly.
     // No locking, as this happens before any background thread is started.
     boost::signals2::connection block_notify_genesis_wait_connection;
-    if (chainman.ActiveChain().Tip() == nullptr) {
+    if (WITH_LOCK(chainman.GetMutex(), return chainman.ActiveChain().Tip() == nullptr)) {
         block_notify_genesis_wait_connection = uiInterface.NotifyBlockTip_connect(std::bind(BlockNotifyGenesisWait, std::placeholders::_2));
     } else {
         fHaveGenesis = true;
@@ -2804,12 +2804,12 @@ bool AppInitMain(NodeContext& node, interfaces::BlockAndHeaderTipInfo* tip_info)
     // At this point, the RPC is "started", but still in warmup, which means it
     // cannot yet be called. Before we make it callable, we need to make sure
     // that the RPC's view of the best block is valid and consistent with
-    // ChainstateManager's ActiveTip.
+    // ChainstateManager's active tip.
     //
     // If we do not do this, RPC's view of the best block will be height=0 and
     // hash=0x0. This will lead to erroroneous responses for things like
     // waitforblockheight.
-    RPCNotifyBlockChange(chainman.ActiveTip());
+    RPCNotifyBlockChange(WITH_LOCK(chainman.GetMutex(), return chainman.ActiveTip()));
     SetRPCWarmupFinished();
 
     uiInterface.InitMessage(_("Done loading").translated);
```

### src/net_processing.cpp
```diff
@@ -3322,7 +3322,7 @@ void PeerManagerImpl::ProcessHeadersMessage(CNode& pfrom, Peer& peer,
     const std::string msg_type = uses_compressed ? NetMsgType::GETHEADERS2 : NetMsgType::GETHEADERS;
     if (nCount == GetHeadersLimit(pfrom, uses_compressed)) {
         // Headers message had its maximum size; the peer may have more headers.
-        if (MaybeSendGetHeaders(pfrom, msg_type, m_chainman.ActiveChain().GetLocator(pindexLast), peer)) {
+        if (MaybeSendGetHeaders(pfrom, msg_type, WITH_LOCK(m_chainman.GetMutex(), return m_chainman.ActiveChain().GetLocator(pindexLast)), peer)) {
             LogPrint(BCLog::NET, "more %s (%d) to end to peer=%d (startheight:%d)\n",
                     msg_type, pindexLast->nHeight, pfrom.GetId(), peer.m_starting_height);
         }
```

### src/qt/test/wallettests.cpp
```diff
@@ -138,14 +138,14 @@ void TestGUI(interfaces::Node& node)
         if (!wallet->AddWalletDescriptor(w_desc, provider, "", false)) assert(false);
         CTxDestination dest = PKHash(test.coinbaseKey.GetPubKey());
         wallet->SetAddressBook(dest, "", "receive");
-        wallet->SetLastBlockProcessed(105, node.context()->chainman->ActiveChain().Tip()->GetBlockHash());
+        wallet->SetLastBlockProcessed(105, WITH_LOCK(node.context()->chainman->GetMutex(), return node.context()->chainman->ActiveChain().Tip()->GetBlockHash()));
     }
     {
         WalletRescanReserver reserver(*wallet);
         reserver.reserve();
         CWallet::ScanResult result = wallet->ScanForWalletTransactions(Params().GetConsensus().hashGenesisBlock, /*start_height=*/0, /*max_height=*/{}, reserver, /*fUpdate=*/true, /*save_progress=*/false);
         QCOMPARE(result.status, CWallet::ScanResult::SUCCESS);
-        QCOMPARE(result.last_scanned_block, node.context()->chainman->ActiveChain().Tip()->GetBlockHash());
+        QCOMPARE(result.last_scanned_block, WITH_LOCK(node.context()->chainman->GetMutex(), return node.context()->chainman->ActiveChain().Tip()->GetBlockHash()));
         QVERIFY(result.last_failed_block.IsNull());
     }
     wallet->SetBroadcastTransactions(true);
```

### src/rest.cpp
```diff
@@ -821,14 +821,18 @@ static bool rest_getutxos(const CoreContext& context, HTTPRequest* req, const st
     ChainstateManager* maybe_chainman = GetChainman(context, req);
     if (!maybe_chainman) return false;
     ChainstateManager& chainman = *maybe_chainman;
+    decltype(chainman.ActiveHeight()) active_height;
+    uint256 active_hash;
     {
-        auto process_utxos = [&vOutPoints, &outs, &hits](const CCoinsView& view, const CTxMemPool* mempool) {
+        auto process_utxos = [&vOutPoints, &outs, &hits, &active_height, &active_hash, &chainman](const CCoinsView& view, const CTxMemPool* mempool ) EXCLUSIVE_LOCKS_REQUIRED(chainman.GetMutex()) {
             for (const COutPoint& vOutPoint : vOutPoints) {
                 Coin coin;
                 bool hit = (!mempool || !mempool->isSpent(vOutPoint)) && view.GetCoin(vOutPoint, coin);
                 hits.push_back(hit);
                 if (hit) outs.emplace_back(std::move(coin));
             }
+            active_height = chainman.ActiveHeight();
+            active_hash = chainman.ActiveTip()->GetBlockHash();
         };
 
         if (fCheckMemPool) {
@@ -856,7 +860,7 @@ static bool rest_getutxos(const CoreContext& context, HTTPRequest* req, const st
         // serialize data
         // use exact same output as mentioned in Bip64
         CDataStream ssGetUTXOResponse(SER_NETWORK, PROTOCOL_VERSION);
-        ssGetUTXOResponse << chainman.ActiveChain().Height() << chainman.ActiveChain().Tip()->GetBlockHash() << bitmap << outs;
+        ssGetUTXOResponse << active_height << active_hash << bitmap << outs;
         std::string ssGetUTXOResponseString = ssGetUTXOResponse.str();
 
         req->WriteHeader("Content-Type", "application/octet-stream");
@@ -866,7 +870,7 @@ static bool rest_getutxos(const CoreContext& context, HTTPRequest* req, const st
 
     case RESTResponseFormat::HEX: {
         CDataStream ssGetUTXOResponse(SER_NETWORK, PROTOCOL_VERSION);
-        ssGetUTXOResponse << chainman.ActiveChain().Height() << chainman.ActiveChain().Tip()->GetBlockHash() << bitmap << outs;
+        ssGetUTXOResponse << active_height << active_hash << bitmap << outs;
         std::string strHex = HexStr(ssGetUTXOResponse) + "\n";
 
         req->WriteHeader("Content-Type", "text/plain");
@@ -879,8 +883,8 @@ static bool rest_getutxos(const CoreContext& context, HTTPRequest* req, const st
 
         // pack in some essentials
         // use more or less the same output as mentioned in Bip64
-        objGetUTXOResponse.pushKV("chainHeight", chainman.ActiveChain().Height());
-        objGetUTXOResponse.pushKV("chaintipHash", chainman.ActiveChain().Tip()->GetBlockHash().GetHex());
+        objGetUTXOResponse.pushKV("chainHeight", active_height);
+        objGetUTXOResponse.pushKV("chaintipHash", active_hash.GetHex());
         objGetUTXOResponse.pushKV("bitmap", bitmapStringRepresentation);
 
         UniValue utxos(UniValue::VARR);
```

### src/test/interfaces_tests.cpp
```diff
@@ -17,6 +17,7 @@ BOOST_FIXTURE_TEST_SUITE(interfaces_tests, TestChain100Setup)
 
 BOOST_AUTO_TEST_CASE(findBlock)
 {
+    LOCK(Assert(m_node.chainman)->GetMutex());
     auto& chain = m_node.chain;
     const CChain& active = Assert(m_node.chainman)->ActiveChain();
 
@@ -61,6 +62,7 @@ BOOST_AUTO_TEST_CASE(findBlock)
 
 BOOST_AUTO_TEST_CASE(findFirstBlockWithTimeAndHeight)
 {
+    LOCK(Assert(m_node.chainman)->GetMutex());
     auto& chain = m_node.chain;
     const CChain& active = Assert(m_node.chainman)->ActiveChain();
     uint256 hash;
@@ -73,6 +75,7 @@ BOOST_AUTO_TEST_CASE(findFirstBlockWithTimeAndHeight)
 
 BOOST_AUTO_TEST_CASE(findAncestorByHeight)
 {
+    LOCK(Assert(m_node.chainman)->GetMutex());
     auto& chain = m_node.chain;
     const CChain& active = Assert(m_node.chainman)->ActiveChain();
     uint256 hash;
@@ -83,6 +86,7 @@ BOOST_AUTO_TEST_CASE(findAncestorByHeight)
 
 BOOST_AUTO_TEST_CASE(findAncestorByHash)
 {
+    LOCK(Assert(m_node.chainman)->GetMutex());
     auto& chain = m_node.chain;
     const CChain& active = Assert(m_node.chainman)->ActiveChain();
     int height = -1;
@@ -94,7 +98,7 @@ BOOST_AUTO_TEST_CASE(findAncestorByHash)
 BOOST_AUTO_TEST_CASE(findCommonAncestor)
 {
     auto& chain = m_node.chain;
-    const CChain& active = Assert(m_node.chainman)->ActiveChain();
+    const CChain& active = *WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return &Assert(m_node.chainman)->ActiveChain());
     auto* orig_tip = active.Tip();
     for (int i = 0; i < 10; ++i) {
         BlockValidationState state;
```

### src/test/validation_block_tests.cpp
```diff
@@ -267,7 +267,7 @@ BOOST_AUTO_TEST_CASE(mempool_locks_reorg)
 
     // Run the test multiple times
     for (int test_runs = 3; test_runs > 0; --test_runs) {
-        BOOST_CHECK_EQUAL(last_mined->GetHash(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
+        BOOST_CHECK_EQUAL(last_mined->GetHash(), WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain().Tip()->GetBlockHash()));
 
         // Later on split from here
         const uint256 split_hash{last_mined->hashPrevBlock};
@@ -356,7 +356,7 @@ BOOST_AUTO_TEST_CASE(mempool_locks_reorg)
             ProcessBlock(b);
         }
         // Check that the reorg was eventually successful
-        BOOST_CHECK_EQUAL(last_mined->GetHash(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
+        BOOST_CHECK_EQUAL(last_mined->GetHash(), WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain().Tip()->GetBlockHash()));
 
         // We can join the other thread, which returns when the reorg was successful
         rpc_thread.join();
```

### src/test/validation_chainstatemanager_tests.cpp
```diff
@@ -59,12 +59,12 @@ BOOST_AUTO_TEST_CASE(chainstatemanager)
     auto all = manager.GetAll();
     BOOST_CHECK_EQUAL_COLLECTIONS(all.begin(), all.end(), chainstates.begin(), chainstates.end());
 
-    auto& active_chain = manager.ActiveChain();
+    auto& active_chain = WITH_LOCK(manager.GetMutex(), return manager.ActiveChain());
     BOOST_CHECK_EQUAL(&active_chain, &c1.m_chain);
 
-    BOOST_CHECK_EQUAL(manager.ActiveHeight(), -1);
+    BOOST_CHECK_EQUAL(WITH_LOCK(manager.GetMutex(), return manager.ActiveHeight()), -1);
 
-    auto active_tip = manager.ActiveTip();
+    auto active_tip = WITH_LOCK(manager.GetMutex(), return manager.ActiveTip());
     auto exp_tip = c1.m_chain.Tip();
     BOOST_CHECK_EQUAL(active_tip, exp_tip);
 
@@ -103,12 +103,12 @@ BOOST_AUTO_TEST_CASE(chainstatemanager)
     auto all2 = manager.GetAll();
     BOOST_CHECK_EQUAL_COLLECTIONS(all2.begin(), all2.end(), chainstates.begin(), chainstates.end());
 
-    auto& active_chain2 = manager.ActiveChain();
+    auto& active_chain2 = WITH_LOCK(manager.GetMutex(), return manager.ActiveChain());
     BOOST_CHECK_EQUAL(&active_chain2, &c2.m_chain);
 
-    BOOST_CHECK_EQUAL(manager.ActiveHeight(), 0);
+    BOOST_CHECK_EQUAL(WITH_LOCK(manager.GetMutex(), return manager.ActiveHeight()), 0);
 
-    auto active_tip2 = manager.ActiveTip();
+    auto active_tip2 = WITH_LOCK(manager.GetMutex(), return manager.ActiveTip());
     auto exp_tip2 = c2.m_chain.Tip();
     BOOST_CHECK_EQUAL(active_tip2, exp_tip2);
 
@@ -260,7 +260,7 @@ BOOST_FIXTURE_TEST_CASE(chainstatemanager_activate_snapshot, TestChain100Setup)
     BOOST_CHECK(WITH_LOCK(::cs_main, return !chainman.ActiveChain().Genesis()->IsAssumedValid()));
 
     const AssumeutxoData& au_data = *ExpectedAssumeutxo(snapshot_height, ::Params());
-    const CBlockIndex* tip = chainman.ActiveTip();
+    const CBlockIndex* tip = WITH_LOCK(chainman.GetMutex(), return chainman.ActiveTip());
 
     BOOST_CHECK_EQUAL(tip->nChainTx, au_data.nChainTx);
 
@@ -359,7 +359,7 @@ BOOST_FIXTURE_TEST_CASE(chainstatemanager_loadblockindex, TestChain100Setup)
     const int assumed_valid_start_idx = last_assumed_valid_idx - expected_assumed_valid;
 
     CBlockIndex* validated_tip{nullptr};
-    CBlockIndex* assumed_tip{chainman.ActiveChain().Tip()};
+    CBlockIndex* assumed_tip{WITH_LOCK(chainman.GetMutex(), return chainman.ActiveChain().Tip())};
 
     auto reload_all_block_indexes = [&]() {
         for (CChainState* cs : chainman.GetAll()) {
```

### src/validation.h
```diff
@@ -936,6 +936,19 @@ class ChainstateManager
     const CChainParams& GetParams() const { return m_chainparams; }
     const Consensus::Params& GetConsensus() const { return m_chainparams.GetConsensus(); }
 
+    /**
+     * Alias for ::cs_main.
+     * Should be used in new code to make it easier to make ::cs_main a member
+     * of this class.
+     * Generally, methods of this class should be annotated to require this
+     * mutex. This will make calling code more verbose, but also help to:
+     * - Clarify that the method will acquire a mutex that heavily affects
+     *   overall performance.
+     * - Force call sites to think how long they need to acquire the mutex to
+     *   get consistent results.
+     */
+    RecursiveMutex& GetMutex() const LOCK_RETURNED(::cs_main) { return ::cs_main; }
+
     std::thread m_load_block;
     //! A single BlockManager instance is shared across each constructed
     //! chainstate to avoid duplicating block metadata.
@@ -1007,9 +1020,9 @@ class ChainstateManager
 
     //! The most-work chain.
     CChainState& ActiveChainstate() const;
-    CChain& ActiveChain() const { return ActiveChainstate().m_chain; }
-    int ActiveHeight() const { return ActiveChain().Height(); }
-    CBlockIndex* ActiveTip() const { return ActiveChain().Tip(); }
+    CChain& ActiveChain() const EXCLUSIVE_LOCKS_REQUIRED(GetMutex()) { return ActiveChainstate().m_chain; }
+    int ActiveHeight() const EXCLUSIVE_LOCKS_REQUIRED(GetMutex()) { return ActiveChain().Height(); }
+    CBlockIndex* ActiveTip() const EXCLUSIVE_LOCKS_REQUIRED(GetMutex()) { return ActiveChain().Tip(); }
 
     node::BlockMap& BlockIndex() EXCLUSIVE_LOCKS_REQUIRED(::cs_main)
     {
```

### src/wallet/test/availablecoins_tests.cpp
```diff
@@ -43,6 +43,7 @@ class AvailableCoinsTestingSetup : public TestChain100Setup
         CreateAndProcessBlock({CMutableTransaction(blocktx)}, GetScriptForRawPubKey(coinbaseKey.GetPubKey()));
 
         LOCK(wallet->cs_wallet);
+        LOCK(m_node.chainman->GetMutex());
         wallet->SetLastBlockProcessed(wallet->GetLastBlockHeight() + 1, m_node.chainman->ActiveChain().Tip()->GetBlockHash());
         auto it = wallet->mapWallet.find(tx->GetHash());
         BOOST_CHECK(it != wallet->mapWallet.end());
```

### src/wallet/test/spend_tests.cpp
```diff
@@ -17,7 +17,7 @@ BOOST_FIXTURE_TEST_SUITE(spend_tests, WalletTestingSetup)
 BOOST_FIXTURE_TEST_CASE(SubtractFee, TestChain100Setup)
 {
     CreateAndProcessBlock({}, GetScriptForRawPubKey(coinbaseKey.GetPubKey()));
-    auto wallet = CreateSyncedWallet(*m_node.chain, *m_node.coinjoin_loader, m_node.chainman->ActiveChain(), m_args, coinbaseKey);
+    auto wallet = CreateSyncedWallet(*m_node.chain, *m_node.coinjoin_loader, WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain()), m_args, coinbaseKey);
 
     // Check that a subtract-from-recipient transaction slightly less than the
     // coinbase input amount does not create a change output (because it would
```

### src/wallet/test/wallet_tests.cpp
```diff
@@ -105,17 +105,18 @@ static void AddKey(CWallet& wallet, const CKey& key)
 BOOST_FIXTURE_TEST_CASE(scan_for_wallet_transactions, TestChain100Setup)
 {
     // Cap last block file size, and mine new block in a new block file.
-    CBlockIndex* oldTip = m_node.chainman->ActiveChain().Tip();
+    CBlockIndex* oldTip = WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain().Tip());
     WITH_LOCK(::cs_main, m_node.chainman->m_blockman.GetBlockFileInfo(oldTip->GetBlockPos().nFile)->nSize = MAX_BLOCKFILE_SIZE);
     CreateAndProcessBlock({}, GetScriptForRawPubKey(coinbaseKey.GetPubKey()));
-    CBlockIndex* newTip = m_node.chainman->ActiveChain().Tip();
+    CBlockIndex* newTip = WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain().Tip());
 
     // Verify ScanForWalletTransactions fails to read an unknown start block.
     {
         CWallet wallet(m_node.chain.get(), m_node.coinjoin_loader.get(), "", m_args, CreateDummyWalletDatabase());
         wallet.SetupLegacyScriptPubKeyMan();
         {
             LOCK(wallet.cs_wallet);
+            LOCK(Assert(m_node.chainman)->GetMutex());
             wallet.SetWalletFlag(WALLET_FLAG_DESCRIPTORS);
             wallet.SetLastBlockProcessed(m_node.chainman->ActiveChain().Height(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
         }
@@ -136,6 +137,7 @@ BOOST_FIXTURE_TEST_CASE(scan_for_wallet_transactions, TestChain100Setup)
         CWallet wallet(m_node.chain.get(), m_node.coinjoin_loader.get(), "", m_args, CreateMockWalletDatabase());
         {
             LOCK(wallet.cs_wallet);
+            LOCK(Assert(m_node.chainman)->GetMutex());
             wallet.SetWalletFlag(WALLET_FLAG_DESCRIPTORS);
             wallet.SetLastBlockProcessed(m_node.chainman->ActiveChain().Height(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
         }
@@ -180,6 +182,7 @@ BOOST_FIXTURE_TEST_CASE(scan_for_wallet_transactions, TestChain100Setup)
         CWallet wallet(m_node.chain.get(), m_node.coinjoin_loader.get(), "", m_args, CreateDummyWalletDatabase());
         {
             LOCK(wallet.cs_wallet);
+            LOCK(Assert(m_node.chainman)->GetMutex());
             wallet.SetWalletFlag(WALLET_FLAG_DESCRIPTORS);
             wallet.SetLastBlockProcessed(m_node.chainman->ActiveChain().Height(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
         }
@@ -207,6 +210,7 @@ BOOST_FIXTURE_TEST_CASE(scan_for_wallet_transactions, TestChain100Setup)
         CWallet wallet(m_node.chain.get(), m_node.coinjoin_loader.get(), "", m_args, CreateDummyWalletDatabase());
         {
             LOCK(wallet.cs_wallet);
+            LOCK(Assert(m_node.chainman)->GetMutex());
             wallet.SetWalletFlag(WALLET_FLAG_DESCRIPTORS);
             wallet.SetLastBlockProcessed(m_node.chainman->ActiveChain().Height(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
         }
@@ -225,10 +229,10 @@ BOOST_FIXTURE_TEST_CASE(scan_for_wallet_transactions, TestChain100Setup)
 BOOST_FIXTURE_TEST_CASE(importmulti_rescan, TestChain100Setup)
 {
     // Cap last block file size, and mine new block in a new block file.
-    CBlockIndex* oldTip = m_node.chainman->ActiveChain().Tip();
+    CBlockIndex* oldTip = WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain().Tip());
     WITH_LOCK(::cs_main, m_node.chainman->m_blockman.GetBlockFileInfo(oldTip->GetBlockPos().nFile)->nSize = MAX_BLOCKFILE_SIZE);
     CreateAndProcessBlock({}, GetScriptForRawPubKey(coinbaseKey.GetPubKey()));
-    CBlockIndex* newTip = m_node.chainman->ActiveChain().Tip();
+    CBlockIndex* newTip = WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain().Tip());
 
     // Prune the older block file.
     int file_number;
@@ -291,7 +295,7 @@ BOOST_FIXTURE_TEST_CASE(importwallet_rescan, TestChain100Setup)
 {
     // Create two blocks with same timestamp to verify that importwallet rescan
     // will pick up both blocks, not just the first.
-    const int64_t BLOCK_TIME = m_node.chainman->ActiveChain().Tip()->GetBlockTimeMax() + 5;
+    const int64_t BLOCK_TIME = WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain().Tip()->GetBlockTimeMax() + 5);
     SetMockTime(BLOCK_TIME);
     m_coinbase_txns.emplace_back(CreateAndProcessBlock({}, GetScriptForRawPubKey(coinbaseKey.GetPubKey())).vtx[0]);
     m_coinbase_txns.emplace_back(CreateAndProcessBlock({}, GetScriptForRawPubKey(coinbaseKey.GetPubKey())).vtx[0]);
@@ -316,6 +320,7 @@ BOOST_FIXTURE_TEST_CASE(importwallet_rescan, TestChain100Setup)
             spk_man->AddKeyPubKey(coinbaseKey, coinbaseKey.GetPubKey());
 
             AddWallet(context, wallet);
+            LOCK(Assert(m_node.chainman)->GetMutex());
             wallet->SetLastBlockProcessed(m_node.chainman->ActiveChain().Height(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
         }
         JSONRPCRequest request;
@@ -341,6 +346,7 @@ BOOST_FIXTURE_TEST_CASE(importwallet_rescan, TestChain100Setup)
         request.params.setArray();
         request.params.push_back(backup_file);
         AddWallet(context, wallet);
+        LOCK(Assert(m_node.chainman)->GetMutex());
         wallet->SetLastBlockProcessed(m_node.chainman->ActiveChain().Height(), m_node.chainman->ActiveChain().Tip()->GetBlockHash());
         wallet::importwallet().HandleRequest(request);
         RemoveWallet(context, wallet, /*load_on_start=*/std::nullopt);
@@ -364,9 +370,9 @@ BOOST_FIXTURE_TEST_CASE(importwallet_rescan, TestChain100Setup)
 BOOST_FIXTURE_TEST_CASE(coin_mark_dirty_immature_credit, TestChain100Setup)
 {
     CWallet wallet(m_node.chain.get(), m_node.coinjoin_loader.get(), "", m_args, CreateDummyWalletDatabase());
-    CWalletTx wtx{m_coinbase_txns.back(), TxStateConfirmed{m_node.chainman->ActiveChain().Tip()->GetBlockHash(), m_node.chainman->ActiveChain().Height(), /*index=*/0}};
-
     LOCK(wallet.cs_wallet);
+    LOCK(Assert(m_node.chainman)->GetMutex());
+    CWalletTx wtx{m_coinbase_txns.back(), TxStateConfirmed{m_node.chainman->ActiveChain().Tip()->GetBlockHash(), m_node.chainman->ActiveChain().Height(), /*index=*/0}};
     wallet.SetWalletFlag(WALLET_FLAG_DESCRIPTORS);
     wallet.SetupDescriptorScriptPubKeyMans("", "");
 
@@ -578,7 +584,7 @@ class ListCoinsTestingSetup : public TestChain100Setup
     ListCoinsTestingSetup()
     {
         CreateAndProcessBlock({}, GetScriptForRawPubKey(coinbaseKey.GetPubKey()));
-        wallet = CreateSyncedWallet(*m_node.chain, *m_node.coinjoin_loader, m_node.chainman->ActiveChain(), m_args, coinbaseKey);
+        wallet = CreateSyncedWallet(*m_node.chain, *m_node.coinjoin_loader, WITH_LOCK(Assert(m_node.chainman)->GetMutex(), return m_node.chainman->ActiveChain()), m_args, coinbaseKey);
     }
 
     ~ListCoinsTestingSetup()
@@ -604,6 +610,7 @@ class ListCoinsTestingSetup : public TestChain100Setup
         CreateAndProcessBlock({CMutableTransaction(blocktx)}, GetScriptForRawPubKey(coinbaseKey.GetPubKey()));
 
         LOCK(wallet->cs_wallet);
+        LOCK(Assert(m_node.chainman)->GetMutex());
         wallet->SetLastBlockProcessed(wallet->GetLastBlockHeight() + 1, m_node.chainman->ActiveChain().Tip()->GetBlockHash());
         auto it = wallet->mapWallet.find(tx->GetHash());
         BOOST_CHECK(it != wallet->mapWallet.end());
```
