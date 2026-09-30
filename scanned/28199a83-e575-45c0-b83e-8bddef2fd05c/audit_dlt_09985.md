# [?] Fix wallet unload race condition

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-03-10
Source: https://github.com/litecoin-project/litecoin/commit/ab31b9d6fe7b39713682e3f52d11238dbe042c16
Type: security-commit

## Details
Fix wallet unload race condition

Currently it's possible for ReleaseWallet to delete the CWallet pointer while
it is processing BlockConnected, etc chain notifications.

To fix this, unregister from notifications earlier in UnloadWallet instead of
ReleaseWallet, and use a new RegisterSharedValidationInterface function to
prevent the CValidationInterface shared_ptr from being deleted until the last
notification is actually finished.

## Patch
### src/bench/wallet_balance.cpp
```diff
@@ -23,9 +23,8 @@ static void WalletBalance(benchmark::State& state, const bool set_dirty, const b
         wallet.SetupLegacyScriptPubKeyMan();
         bool first_run;
         if (wallet.LoadWallet(first_run) != DBErrors::LOAD_OK) assert(false);
-        wallet.handleNotifications();
     }
-
+    auto handler = chain->handleNotifications({ &wallet, [](CWallet*) {} });
 
     const Optional<std::string> address_mine{add_mine ? Optional<std::string>{getnewaddress(wallet)} : nullopt};
     if (add_watchonly) importaddress(wallet, ADDRESS_WATCHONLY);
```

### src/interfaces/chain.cpp
```diff
@@ -148,22 +148,12 @@ class LockImpl : public Chain::Lock, public UniqueLock<RecursiveMutex>
     using UniqueLock::UniqueLock;
 };
 
-class NotificationsHandlerImpl : public Handler, CValidationInterface
+class NotificationsProxy : public CValidationInterface
 {
 public:
-    explicit NotificationsHandlerImpl(Chain& chain, Chain::Notifications& notifications)
-        : m_chain(chain), m_notifications(&notifications)
-    {
-        RegisterValidationInterface(this);
-    }
-    ~NotificationsHandlerImpl() override { disconnect(); }
-    void disconnect() override
-    {
-        if (m_notifications) {
-            m_notifications = nullptr;
-            UnregisterValidationInterface(this);
-        }
-    }
+    explicit NotificationsProxy(std::shared_ptr<Chain::Notifications> notifications)
+        : m_notifications(std::move(notifications)) {}
+    virtual ~NotificationsProxy() = default;
     void TransactionAddedToMempool(const CTransactionRef& tx) override
     {
         m_notifications->transactionAddedToMempool(tx);
@@ -185,8 +175,26 @@ class NotificationsHandlerImpl : public Handler, CValidationInterface
         m_notifications->updatedBlockTip();
     }
     void ChainStateFlushed(const CBlockLocator& locator) override { m_notifications->chainStateFlushed(locator); }
-    Chain& m_chain;
-    Chain::Notifications* m_notifications;
+    std::shared_ptr<Chain::Notifications> m_notifications;
+};
+
+class NotificationsHandlerImpl : public Handler
+{
+public:
+    explicit NotificationsHandlerImpl(std::shared_ptr<Chain::Notifications> notifications)
+        : m_proxy(std::make_shared<NotificationsProxy>(std::move(notifications)))
+    {
+        RegisterSharedValidationInterface(m_proxy);
+    }
+    ~NotificationsHandlerImpl() override { disconnect(); }
+    void disconnect() override
+    {
+        if (m_proxy) {
+            UnregisterSharedValidationInterface(m_proxy);
+            m_proxy.reset();
+        }
+    }
+    std::shared_ptr<NotificationsProxy> m_proxy;
 };
 
 class RpcHandlerImpl : public Handler
@@ -343,9 +351,9 @@ class ChainImpl : public Chain
     {
         ::uiInterface.ShowProgress(title, progress, resume_possible);
     }
-    std::unique_ptr<Handler> handleNotifications(Notifications& notifications) override
+    std::unique_ptr<Handler> handleNotifications(std::shared_ptr<Notifications> notifications) override
     {
-        return MakeUnique<NotificationsHandlerImpl>(*this, notifications);
+        return MakeUnique<NotificationsHandlerImpl>(std::move(notifications));
     }
     void waitForNotificationsIfTipChanged(const uint256& old_tip) override
     {
```

### src/interfaces/chain.h
```diff
@@ -229,7 +229,7 @@ class Chain
     };
 
     //! Register handler for notifications.
-    virtual std::unique_ptr<Handler> handleNotifications(Notifications& notifications) = 0;
+    virtual std::unique_ptr<Handler> handleNotifications(std::shared_ptr<Notifications> notifications) = 0;
 
     //! Wait for pending notifications to be processed unless block hash points to the current
     //! chain tip.
```

### src/validationinterface.cpp
```diff
@@ -75,8 +75,10 @@ CMainSignals& GetMainSignals()
     return g_signals;
 }
 
-void RegisterValidationInterface(CValidationInterface* pwalletIn) {
-    ValidationInterfaceConnections& conns = g_signals.m_internals->m_connMainSignals[pwalletIn];
+void RegisterSharedValidationInterface(std::shared_ptr<CValidationInterface> pwalletIn) {
+    // Each connection captures pwalletIn to ensure that each callback is
+    // executed before pwalletIn is destroyed. For more details see #18338.
+    ValidationInterfaceConnections& conns = g_signals.m_internals->m_connMainSignals[pwalletIn.get()];
     conns.UpdatedBlockTip = g_signals.m_internals->UpdatedBlockTip.connect(std::bind(&CValidationInterface::UpdatedBlockTip, pwalletIn, std::placeholders::_1, std::placeholders::_2, std::placeholders::_3));
     conns.TransactionAddedToMempool = g_signals.m_internals->TransactionAddedToMempool.connect(std::bind(&CValidationInterface::TransactionAddedToMempool, pwalletIn, std::placeholders::_1));
     conns.BlockConnected = g_signals.m_internals->BlockConnected.connect(std::bind(&CValidationInterface::BlockConnected, pwalletIn, std::placeholders::_1, std::placeholders::_2));
@@ -87,6 +89,18 @@ void RegisterValidationInterface(CValidationInterface* pwalletIn) {
     conns.NewPoWValidBlock = g_signals.m_internals->NewPoWValidBlock.connect(std::bind(&CValidationInterface::NewPoWValidBlock, pwalletIn, std::placeholders::_1, std::placeholders::_2));
 }
 
+void RegisterValidationInterface(CValidationInterface* callbacks)
+{
+    // Create a shared_ptr with a no-op deleter - CValidationInterface lifecycle
+    // is managed by the caller.
+    RegisterSharedValidationInterface({callbacks, [](CValidationInterface*){}});
+}
+
+void UnregisterSharedValidationInterface(std::shared_ptr<CValidationInterface> callbacks)
+{
+    UnregisterValidationInterface(callbacks.get());
+}
+
 void UnregisterValidationInterface(CValidationInterface* pwalletIn) {
     if (g_signals.m_internals) {
         g_signals.m_internals->m_connMainSignals.erase(pwalletIn);
```

### src/validationinterface.h
```diff
@@ -30,6 +30,14 @@ void RegisterValidationInterface(CValidationInterface* pwalletIn);
 void UnregisterValidationInterface(CValidationInterface* pwalletIn);
 /** Unregister all wallets from core */
 void UnregisterAllValidationInterfaces();
+
+// Alternate registration functions that release a shared_ptr after the last
+// notification is sent. These are useful for race-free cleanup, since
+// unregistration is nonblocking and can return before the last notification is
+// processed.
+void RegisterSharedValidationInterface(std::shared_ptr<CValidationInterface> callbacks);
+void UnregisterSharedValidationInterface(std::shared_ptr<CValidationInterface> callbacks);
+
 /**
  * Pushes a function to callback onto the notification queue, guaranteeing any
  * callbacks generated prior to now are finished when the function is called.
@@ -163,7 +171,7 @@ class CValidationInterface {
      * Notifies listeners that a block which builds directly on our current tip
      * has been received and connected to the headers tree, though not validated yet */
     virtual void NewPoWValidBlock(const CBlockIndex *pindex, const std::shared_ptr<const CBlock>& block) {};
-    friend void ::RegisterValidationInterface(CValidationInterface*);
+    friend void ::RegisterSharedValidationInterface(std::shared_ptr<CValidationInterface>);
     friend void ::UnregisterValidationInterface(CValidationInterface*);
     friend void ::UnregisterAllValidationInterfaces();
 };
@@ -173,7 +181,7 @@ class CMainSignals {
 private:
     std::unique_ptr<MainSignalsInstance> m_internals;
 
-    friend void ::RegisterValidationInterface(CValidationInterface*);
+    friend void ::RegisterSharedValidationInterface(std::shared_ptr<CValidationInterface>);
     friend void ::UnregisterValidationInterface(CValidationInterface*);
     friend void ::UnregisterAllValidationInterfaces();
     friend void ::CallFunctionInValidationInterfaceQueue(std::function<void ()> func);
```

### src/wallet/test/wallet_test_fixture.cpp
```diff
@@ -10,7 +10,6 @@ WalletTestingSetup::WalletTestingSetup(const std::string& chainName)
 {
     bool fFirstRun;
     m_wallet.LoadWallet(fFirstRun);
-    m_wallet.handleNotifications();
-
+    m_chain_notifications_handler = m_chain->handleNotifications({ &m_wallet, [](CWallet*) {} });
     m_chain_client->registerRpcs();
 }
```

### src/wallet/test/wallet_test_fixture.h
```diff
@@ -23,6 +23,7 @@ struct WalletTestingSetup: public TestingSetup {
     std::unique_ptr<interfaces::Chain> m_chain = interfaces::MakeChain(m_node);
     std::unique_ptr<interfaces::ChainClient> m_chain_client = interfaces::MakeWalletClient(*m_chain, {});
     CWallet m_wallet;
+    std::unique_ptr<interfaces::Handler> m_chain_notifications_handler;
 };
 
 #endif // BITCOIN_WALLET_TEST_WALLET_TEST_FIXTURE_H
```

### src/wallet/wallet.cpp
```diff
@@ -62,8 +62,10 @@ bool AddWallet(const std::shared_ptr<CWallet>& wallet)
 
 bool RemoveWallet(const std::shared_ptr<CWallet>& wallet)
 {
-    LOCK(cs_wallets);
     assert(wallet);
+    // Unregister with the validation interface which also drops shared ponters.
+    wallet->m_chain_notifications_handler.reset();
+    LOCK(cs_wallets);
     std::vector<std::shared_ptr<CWallet>>::iterator i = std::find(vpwallets.begin(), vpwallets.end(), wallet);
     if (i == vpwallets.end()) return false;
     vpwallets.erase(i);
@@ -105,13 +107,9 @@ static std::set<std::string> g_unloading_wallet_set;
 // Custom deleter for shared_ptr<CWallet>.
 static void ReleaseWallet(CWallet* wallet)
 {
-    // Unregister and delete the wallet right after BlockUntilSyncedToCurrentChain
-    // so that it's in sync with the current chainstate.
     const std::string name = wallet->GetName();
     wallet->WalletLogPrintf("Releasing wallet\n");
-    wallet->BlockUntilSyncedToCurrentChain();
     wallet->Flush();
-    wallet->m_chain_notifications_handler.reset();
     delete wallet;
     // Wallet is now released, notify UnloadWallet, if any.
     {
@@ -137,6 +135,7 @@ void UnloadWallet(std::shared_ptr<CWallet>&& wallet)
     // Notify the unload intent so that all remaining shared pointers are
     // released.
     wallet->NotifyUnload();
+
     // Time to ditch our shared_ptr and wait for ReleaseWallet call.
     wallet.reset();
     {
@@ -4092,7 +4091,7 @@ std::shared_ptr<CWallet> CWallet::CreateWalletFromFile(interfaces::Chain& chain,
     }
 
     // Register with the validation interface. It's ok to do this after rescan since we're still holding locked_chain.
-    walletInstance->handleNotifications();
+    walletInstance->m_chain_notifications_handler = walletInstance->chain().handleNotifications(walletInstance);
 
     walletInstance->SetBroadcastTransactions(gArgs.GetBoolArg("-walletbroadcast", DEFAULT_WALLETBROADCAST));
 
@@ -4105,11 +4104,6 @@ std::shared_ptr<CWallet> CWallet::CreateWalletFromFile(interfaces::Chain& chain,
     return walletInstance;
 }
 
-void CWallet::handleNotifications()
-{
-    m_chain_notifications_handler = m_chain->handleNotifications(*this);
-}
-
 void CWallet::postInitProcess()
 {
     auto locked_chain = chain().lock();
```

### src/wallet/wallet.h
```diff
@@ -605,7 +605,7 @@ class WalletRescanReserver; //forward declarations for ScanForWalletTransactions
 /**
  * A CWallet maintains a set of transactions and balances, and provides the ability to create new transactions.
  */
-class CWallet final : public WalletStorage, private interfaces::Chain::Notifications
+class CWallet final : public WalletStorage, public interfaces::Chain::Notifications
 {
 private:
     CKeyingMaterial vMasterKey GUARDED_BY(cs_wallet);
@@ -781,9 +781,6 @@ class CWallet final : public WalletStorage, private interfaces::Chain::Notificat
     /** Registered interfaces::Chain::Notifications handler. */
     std::unique_ptr<interfaces::Handler> m_chain_notifications_handler;
 
-    /** Register the wallet for chain notifications */
-    void handleNotifications();
-
     /** Interface for accessing chain state. */
     interfaces::Chain& chain() const { assert(m_chain); return *m_chain; }
 
```
