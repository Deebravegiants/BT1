# [?] fix: crash due to unitialized variable if no blocks has been mined yet

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-01-23
Source: https://github.com/dashpay/dash/commit/5422b0aef6360d10c0df5f04e5a2aaea58302a05
Type: security-commit

## Details
fix: crash due to unitialized variable if no blocks has been mined yet

     ~/projects/dash/src/qt/dash-qt -regtest -datadir=/tmp/dd
    ERROR: error detected null not_null detected at qt/masternodelist.cpp:167:0:updateDIP3List
    std::terminate() called due unknown reason
       0#: (0x555DEA157622) stl_vector.h:768       - std::vector<unsigned long, std::allocator<unsigned long> >::operator=(std::vector<unsigned long, std::allocator<unsigned long> >&&)
       1#: (0x555DEA157622) stacktraces.cpp:747    - terminate_handler
       2#: (0x76A37E2B6E6C) <unknown-file>         - ???
       3#: (0x76A37E2B6ED7) <unknown-file>         - ???
       4#: (0x555DE9B43887) logging.h:156          - BCLog::Logger::Enabled() const
       5#: (0x555DE9B43887) logging.h:263          - LogPrintf_<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >
       6#: (0x555DE9B43887) assert.cpp:36          - gsl::details::terminate(nostd::source_location)
       7#: (0x555DE9A5314D) pointers.h:110         - gsl::not_null<CBlockIndex const* const>::not_null<void>(CBlockIndex const*, nostd::source_location)
       8#: (0x555DE9A5314D) masternodelist.cpp:167 - MasternodeList::updateDIP3List()
       9#: (0x555DE9A53678) masternodelist.cpp:147 - MasternodeList::updateDIP3ListScheduled()
      10#: (0x555DEAB42F5D) <unknown-file>         - ???
      11#: (0x555DEAB4B261) <unknown-file>         - ???
      12#: (0x555DEAB3D48B) <unknown-file>         - ???
      13#: (0x555DEADC1DF2) <unknown-file>         - ???
      14#: (0x555DEAB169F8) <unknown-file>         - ???
      15#: (0x555DEAB66F5D) <unknown-file>         - ???
      16#: (0x555DEAB64E84) <unknown-file>         - ???
      17#: (0x555DEACBCE22) <unknown-file>         - ???
      18#: (0x555DEAB14E56) <unknown-file>         - ???

## Patch
### src/qt/clientmodel.h
```diff
@@ -122,7 +122,7 @@ class ClientModel : public QObject
     // representation of the list in UI during initial sync/reindex, so we cache it here too.
     mutable RecursiveMutex cs_mnlinst; // protects mnListCached
     CDeterministicMNListPtr mnListCached;
-    const CBlockIndex* mnListTip;
+    const CBlockIndex* mnListTip{nullptr};
 
     void subscribeToCoreSignals();
     void unsubscribeFromCoreSignals();
```

### src/qt/masternodelist.cpp
```diff
@@ -164,6 +164,7 @@ void MasternodeList::updateDIP3List()
     }
 
     auto [mnList, pindex] = clientModel->getMasternodeList();
+    if (!pindex) return;
     auto projectedPayees = mnList.GetProjectedMNPayees(pindex);
 
     if (projectedPayees.empty() && mnList.GetValidMNsCount() > 0) {
```
