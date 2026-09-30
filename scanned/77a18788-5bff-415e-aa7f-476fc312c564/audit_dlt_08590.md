# [?] Prevent deadlock in storeSQLite

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2020-12-01
Source: https://github.com/XRPLF/rippled/commit/1fd1c341123111b370c92b38f0e11ca994a74f2a
Type: security-commit

## Details
Prevent deadlock in storeSQLite

## Patch
### src/ripple/app/main/DBInit.h
```diff
@@ -129,9 +129,9 @@ inline constexpr std::array<char const*, 1> AcquireShardDBInit{
 
 ////////////////////////////////////////////////////////////////////////////////
 
-// Pragma for Ledger and Transaction databases with complete shards
+// Pragma for Ledger and Transaction databases with final shards
 // These override the CommonDBPragma values defined above.
-inline constexpr std::array<char const*, 2> CompleteShardDBPragma{
+inline constexpr std::array<char const*, 2> FinalShardDBPragma{
     {"PRAGMA synchronous=OFF;", "PRAGMA journal_mode=OFF;"}};
 
 ////////////////////////////////////////////////////////////////////////////////
```

### src/ripple/nodestore/impl/Shard.cpp
```diff
@@ -429,38 +429,77 @@ Shard::setLedgerStored(std::shared_ptr<Ledger const> const& ledger)
         return false;
     }
 
-    std::lock_guard lock(mutex_);
-    if (!acquireInfo_)
-    {
-        JLOG(j_.error()) << "shard " << index_
-                         << " missing acquire SQLite database";
+    auto const scopedCount{makeBackendCount()};
+    if (!scopedCount)
         return false;
-    }
-    if (boost::icl::contains(acquireInfo_->storedSeqs, ledgerSeq))
+
+    // This lock is used as an optimization to prevent unneeded
+    // calls to storeSQLite before acquireInfo_ is updated
+    std::lock_guard storedLock(storedMutex_);
+
     {
-        // Ignore redundant calls
-        JLOG(j_.debug()) << "shard " << index_ << " ledger sequence "
-                         << ledgerSeq << " already stored";
-        return true;
+        std::lock_guard lock(mutex_);
+        if (!acquireInfo_)
+        {
+            JLOG(j_.error())
+                << "shard " << index_ << " missing acquire SQLite database";
+            return false;
+        }
+        if (boost::icl::contains(acquireInfo_->storedSeqs, ledgerSeq))
+        {
+            // Ignore redundant calls
+            JLOG(j_.debug()) << "shard " << index_ << " ledger sequence "
+                             << ledgerSeq << " already stored";
+            return true;
+        }
     }
-    // storeSQLite looks at storedSeqs so insert before the call
-    acquireInfo_->storedSeqs.insert(ledgerSeq);
 
-    if (!storeSQLite(ledger, lock))
+    if (!storeSQLite(ledger))
         return false;
 
-    if (boost::icl::length(acquireInfo_->storedSeqs) >= maxLedgers_)
-    {
-        if (!initSQLite(lock))
-            return false;
+    std::lock_guard lock(mutex_);
 
-        state_ = complete;
+    // Update the acquire database
+    acquireInfo_->storedSeqs.insert(ledgerSeq);
+
+    try
+    {
+        auto session{acquireInfo_->SQLiteDB->checkoutDb()};
+        soci::blob sociBlob(*session);
+        convert(to_string(acquireInfo_->storedSeqs), sociBlob);
+        if (ledgerSeq == lastSeq_)
+        {
+            // Store shard's last ledger hash
+            auto const sHash{to_string(ledger->info().hash)};
+            *session << "UPDATE Shard "
+                        "SET LastLedgerHash = :lastLedgerHash,"
+                        "StoredLedgerSeqs = :storedLedgerSeqs "
+                        "WHERE ShardIndex = :shardIndex;",
+                soci::use(sHash), soci::use(sociBlob), soci::use(index_);
+        }
+        else
+        {
+            *session << "UPDATE Shard "
+                        "SET StoredLedgerSeqs = :storedLedgerSeqs "
+                        "WHERE ShardIndex = :shardIndex;",
+                soci::use(sociBlob), soci::use(index_);
+        }
+    }
+    catch (std::exception const& e)
+    {
+        JLOG(j_.fatal()) << "shard " << index_
+                         << ". Exception caught in function " << __func__
+                         << ". Error: " << e.what();
+        acquireInfo_->storedSeqs.erase(ledgerSeq);
+        return false;
     }
 
-    JLOG(j_.debug()) << "shard " << index_ << " stored ledger sequence "
-                     << ledgerSeq;
+    if (boost::icl::length(acquireInfo_->storedSeqs) >= maxLedgers_)
+        state_ = complete;
 
     setFileStats(lock);
+    JLOG(j_.trace()) << "shard " << index_ << " stored ledger sequence "
+                     << ledgerSeq;
     return true;
 }
 
@@ -525,16 +564,16 @@ Shard::finalize(
 {
     uint256 hash{0};
     std::uint32_t ledgerSeq{0};
-    auto fail =
-        [j = j_, index = index_, &hash, &ledgerSeq](std::string const& msg) {
-            JLOG(j.fatal())
-                << "shard " << index << ". " << msg
-                << (hash.isZero() ? "" : ". Ledger hash " + to_string(hash))
-                << (ledgerSeq == 0
-                        ? ""
-                        : ". Ledger sequence " + std::to_string(ledgerSeq));
-            return false;
-        };
+    auto fail = [&](std::string const& msg) {
+        JLOG(j_.fatal()) << "shard " << index_ << ". " << msg
+                         << (hash.isZero() ? ""
+                                           : ". Ledger hash " + to_string(hash))
+                         << (ledgerSeq == 0 ? ""
+                                            : ". Ledger sequence " +
+                                     std::to_string(ledgerSeq));
+        state_ = finalizing;
+        return false;
+    };
 
     auto const scopedCount{makeBackendCount()};
     if (!scopedCount)
@@ -578,14 +617,14 @@ Shard::finalize(
             if (!acquireInfo_)
                 return fail("missing acquire SQLite database");
 
-            auto& session{acquireInfo_->SQLiteDB->getSession()};
+            auto session{acquireInfo_->SQLiteDB->checkoutDb()};
             boost::optional<std::uint32_t> index;
             boost::optional<std::string> sHash;
-            soci::blob sociBlob(session);
+            soci::blob sociBlob(*session);
             soci::indicator blobPresent;
-            session << "SELECT ShardIndex, LastLedgerHash, StoredLedgerSeqs "
-                       "FROM Shard "
-                       "WHERE ShardIndex = :index;",
+            *session << "SELECT ShardIndex, LastLedgerHash, StoredLedgerSeqs "
+                        "FROM Shard "
+                        "WHERE ShardIndex = :index;",
                 soci::into(index), soci::into(sHash),
                 soci::into(sociBlob, blobPresent), soci::use(index_);
 
@@ -678,12 +717,8 @@ Shard::finalize(
         if (!verifyLedger(ledger, next))
             return fail("failed to validate ledger");
 
-        if (writeSQLite)
-        {
-            std::lock_guard lock(mutex_);
-            if (!storeSQLite(ledger, lock))
-                return fail("failed storing to SQLite databases");
-        }
+        if (writeSQLite && !storeSQLite(ledger))
+            return fail("failed storing to SQLite databases");
 
         hash = ledger->info().parentHash;
         next = std::move(ledger);
@@ -710,12 +745,12 @@ Shard::finalize(
 
         auto vacuum = [&tmpDir](std::unique_ptr<DatabaseCon>& sqliteDB)
         {
-            auto& session {sqliteDB->getSession()};
-            session << "PRAGMA synchronous=OFF;";
-            session << "PRAGMA journal_mode=OFF;";
-            session << "PRAGMA temp_store_directory='" <<
+            auto session {sqliteDB->checkoutDb()};
+            *session << "PRAGMA synchronous=OFF;";
+            *session << "PRAGMA journal_mode=OFF;";
+            *session << "PRAGMA temp_store_directory='" <<
                 tmpDir.string() << "';";
-            session << "VACUUM;";
+            *session << "VACUUM;";
         };
         vacuum(lgrSQLiteDB_);
         vacuum(txSQLiteDB_);
@@ -750,11 +785,13 @@ Shard::finalize(
             remove_all(dir_ / AcquireShardDBName);
         }
 
+        lastAccess_ = std::chrono::steady_clock::now();
+        state_ = final;
+
         if (!initSQLite(lock))
             return fail("failed to initialize SQLite databases");
 
         setFileStats(lock);
-        lastAccess_ = std::chrono::steady_clock::now();
     }
     catch (std::exception const& e)
     {
@@ -763,7 +800,6 @@ Shard::finalize(
             ". Error: " + e.what());
     }
 
-    state_ = final;
     return true;
 }
 
@@ -927,25 +963,25 @@ Shard::initSQLite(std::lock_guard<std::mutex> const&)
         if (txSQLiteDB_)
             txSQLiteDB_.reset();
 
-        if (state_ != acquire)
+        if (state_ == final)
         {
             lgrSQLiteDB_ = std::make_unique<DatabaseCon>(
-                setup, LgrDBName, CompleteShardDBPragma, LgrDBInit);
+                setup, LgrDBName, FinalShardDBPragma, LgrDBInit);
             lgrSQLiteDB_->getSession() << boost::str(
                 boost::format("PRAGMA cache_size=-%d;") %
                 kilobytes(
                     config.getValueFor(SizedItem::lgrDBCache, boost::none)));
 
             txSQLiteDB_ = std::make_unique<DatabaseCon>(
-                setup, TxDBName, CompleteShardDBPragma, TxDBInit);
+                setup, TxDBName, FinalShardDBPragma, TxDBInit);
             txSQLiteDB_->getSession() << boost::str(
                 boost::format("PRAGMA cache_size=-%d;") %
                 kilobytes(
                     config.getValueFor(SizedItem::txnDBCache, boost::none)));
         }
         else
         {
-            // The incomplete shard uses a Write Ahead Log for performance
+            // Non final shards use a Write Ahead Log for performance
             lgrSQLiteDB_ = std::make_unique<DatabaseCon>(
                 setup,
                 LgrDBName,
@@ -981,9 +1017,7 @@ Shard::initSQLite(std::lock_guard<std::mutex> const&)
 }
 
 bool
-Shard::storeSQLite(
-    std::shared_ptr<Ledger const> const& ledger,
-    std::lock_guard<std::mutex> const&)
+Shard::storeSQLite(std::shared_ptr<Ledger const> const& ledger)
 {
     if (stop_)
         return false;
@@ -994,14 +1028,14 @@ Shard::storeSQLite(
     {
         // Update the transactions database
         {
-            auto& session{txSQLiteDB_->getSession()};
-            soci::transaction tr(session);
+            auto session{txSQLiteDB_->checkoutDb()};
+            soci::transaction tr(*session);
 
-            session << "DELETE FROM Transactions "
-                       "WHERE LedgerSeq = :seq;",
+            *session << "DELETE FROM Transactions "
+                        "WHERE LedgerSeq = :seq;",
                 soci::use(ledgerSeq);
-            session << "DELETE FROM AccountTransactions "
-                       "WHERE LedgerSeq = :seq;",
+            *session << "DELETE FROM AccountTransactions "
+                        "WHERE LedgerSeq = :seq;",
                 soci::use(ledgerSeq);
 
             if (ledger->info().txHash.isNonZero())
@@ -1025,8 +1059,8 @@ Shard::storeSQLite(
                     auto const txMeta{std::make_shared<TxMeta>(
                         txID, ledger->seq(), *item.second)};
 
-                    session << "DELETE FROM AccountTransactions "
-                               "WHERE TransID = :txID;",
+                    *session << "DELETE FROM AccountTransactions "
+                                "WHERE TransID = :txID;",
                         soci::use(sTxID);
 
                     auto const& accounts = txMeta->getAffectedAccounts(j_);
@@ -1051,7 +1085,7 @@ Shard::storeSQLite(
                                     }),
                             ",");
                         sql += ';';
-                        session << sql;
+                        *session << sql;
 
                         JLOG(j_.trace()) << "shard " << index_
                                          << " account transaction: " << sql;
@@ -1065,7 +1099,7 @@ Shard::storeSQLite(
 
                     Serializer s;
                     item.second->add(s);
-                    session
+                    *session
                         << (STTx::getMetaSQLInsertReplaceHeader() +
                             item.first->getMetaSQL(
                                 ledgerSeq, sqlBlobLiteral(s.modData())) +
@@ -1076,22 +1110,21 @@ Shard::storeSQLite(
             tr.commit();
         }
 
-        auto const sHash{to_string(ledger->info().hash)};
-
         // Update the ledger database
         {
-            auto& session{lgrSQLiteDB_->getSession()};
-            soci::transaction tr(session);
-
             auto const sParentHash{to_string(ledger->info().parentHash)};
             auto const sDrops{to_string(ledger->info().drops)};
             auto const sAccountHash{to_string(ledger->info().accountHash)};
             auto const sTxHash{to_string(ledger->info().txHash)};
+            auto const sHash{to_string(ledger->info().hash)};
 
-            session << "DELETE FROM Ledgers "
-                       "WHERE LedgerSeq = :seq;",
+            auto session{lgrSQLiteDB_->checkoutDb()};
+            soci::transaction tr(*session);
+
+            *session << "DELETE FROM Ledgers "
+                        "WHERE LedgerSeq = :seq;",
                 soci::use(ledgerSeq);
-            session
+            *session
                 << "INSERT OR REPLACE INTO Ledgers ("
                    "LedgerHash, LedgerSeq, PrevHash, TotalCoins, ClosingTime,"
                    "PrevClosingTime, CloseTimeRes, CloseFlags, AccountSetHash,"
@@ -1111,33 +1144,6 @@ Shard::storeSQLite(
 
             tr.commit();
         }
-
-        // Update the acquire database if present
-        if (acquireInfo_)
-        {
-            auto& session{acquireInfo_->SQLiteDB->getSession()};
-            soci::blob sociBlob(session);
-
-            if (!acquireInfo_->storedSeqs.empty())
-                convert(to_string(acquireInfo_->storedSeqs), sociBlob);
-
-            if (ledger->info().seq == lastSeq_)
-            {
-                // Store shard's last ledger hash
-                session << "UPDATE Shard "
-                           "SET LastLedgerHash = :lastLedgerHash,"
-                           "StoredLedgerSeqs = :storedLedgerSeqs "
-                           "WHERE ShardIndex = :shardIndex;",
-                    soci::use(sHash), soci::use(sociBlob), soci::use(index_);
-            }
-            else
-            {
-                session << "UPDATE Shard "
-                           "SET StoredLedgerSeqs = :storedLedgerSeqs "
-                           "WHERE ShardIndex = :shardIndex;",
-                    soci::use(sociBlob), soci::use(index_);
-            }
-        }
     }
     catch (std::exception const& e)
     {
```

### src/ripple/nodestore/impl/Shard.h
```diff
@@ -31,7 +31,6 @@
 #include <nudb/nudb.hpp>
 
 #include <atomic>
-#include <tuple>
 
 namespace ripple {
 namespace NodeStore {
@@ -253,6 +252,7 @@ class Shard final
     Application& app_;
     beast::Journal const j_;
     mutable std::mutex mutex_;
+    mutable std::mutex storedMutex_;
 
     // Shard Index
     std::uint32_t const index_;
@@ -316,11 +316,8 @@ class Shard final
     initSQLite(std::lock_guard<std::mutex> const&);
 
     // Write SQLite entries for this ledger
-    // Lock over mutex_ required
     [[nodiscard]] bool
-    storeSQLite(
-        std::shared_ptr<Ledger const> const& ledger,
-        std::lock_guard<std::mutex> const&);
+    storeSQLite(std::shared_ptr<Ledger const> const& ledger);
 
     // Set storage and file descriptor usage stats
     // Lock over mutex_ required
```
