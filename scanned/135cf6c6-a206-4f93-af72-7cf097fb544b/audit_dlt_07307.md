# [?] Prevent low-likelihood crash on shutdown (RIPD-1392):

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2017-03-07
Source: https://github.com/XRPLF/rippled/commit/9d4500cf6942f651095d5e29a0c0f750d0d383d5
Type: security-commit

## Details
Prevent low-likelihood crash on shutdown (RIPD-1392):

The DatabaseImp has threads that asynchronously call JobQueue to
perform database reads.  Formerly these threads had the same
lifespan as Database, which was until the end-of-life of
ApplicationImp.  During shutdown these threads could call JobQueue
after JobQueue had already stopped.  Or, even worse, occasionally
call JobQueue after JobQueue's destructor had run.

To avoid these shutdown conditions, Database is made a Stoppable,
with JobQueue as its parent.  When Database stops, it shuts down
its asynchronous read threads.  This prevents Database from
accessing JobQueue after JobQueue has stopped, but allows
Database to perform stores for the remainder of shutdown.

During development it was noted that the Database::close()
method was never called.  So that method is removed from Database
and all derived classes.

Stoppable is also adjusted so it can be constructed using either
a char const* or a std::string.

For those files touched for other reasons, unneeded #includes
are removed.

## Patch
### src/ripple/app/main/Application.cpp
```diff
@@ -23,7 +23,6 @@
 #include <ripple/app/main/DBInit.h>
 #include <ripple/app/main/BasicApp.h>
 #include <ripple/app/main/Tuning.h>
-#include <ripple/app/ledger/AcceptedLedger.h>
 #include <ripple/app/ledger/InboundLedgers.h>
 #include <ripple/app/ledger/LedgerMaster.h>
 #include <ripple/app/ledger/LedgerToJson.h>
@@ -32,59 +31,29 @@
 #include <ripple/app/ledger/PendingSaves.h>
 #include <ripple/app/ledger/InboundTransactions.h>
 #include <ripple/app/ledger/TransactionMaster.h>
-#include <ripple/app/main/CollectorManager.h>
 #include <ripple/app/main/LoadManager.h>
 #include <ripple/app/main/NodeIdentity.h>
 #include <ripple/app/main/NodeStoreScheduler.h>
 #include <ripple/app/misc/AmendmentTable.h>
 #include <ripple/app/misc/HashRouter.h>
 #include <ripple/app/misc/LoadFeeTrack.h>
-#include <ripple/app/misc/Manifest.h>
 #include <ripple/app/misc/NetworkOPs.h>
 #include <ripple/app/misc/SHAMapStore.h>
 #include <ripple/app/misc/TxQ.h>
-#include <ripple/app/misc/Validations.h>
-#include <ripple/app/misc/ValidatorList.h>
 #include <ripple/app/misc/ValidatorSite.h>
-#include <ripple/app/paths/Pathfinder.h>
 #include <ripple/app/paths/PathRequests.h>
 #include <ripple/app/tx/apply.h>
-#include <ripple/basics/contract.h>
-#include <ripple/basics/Log.h>
 #include <ripple/basics/ResolverAsio.h>
 #include <ripple/basics/Sustain.h>
-#include <ripple/basics/chrono.h>
 #include <ripple/json/json_reader.h>
-#include <ripple/json/to_string.h>
-#include <ripple/core/ConfigSections.h>
 #include <ripple/core/DeadlineTimer.h>
-#include <ripple/core/TimeKeeper.h>
-#include <ripple/ledger/CachedSLEs.h>
-#include <ripple/nodestore/Database.h>
 #include <ripple/nodestore/DummyScheduler.h>
-#include <ripple/nodestore/Manager.h>
 #include <ripple/overlay/Cluster.h>
 #include <ripple/overlay/make_Overlay.h>
-#include <ripple/protocol/Indexes.h>
-#include <ripple/protocol/PublicKey.h>
-#include <ripple/protocol/SecretKey.h>
 #include <ripple/protocol/STParsedJSON.h>
-#include <ripple/protocol/types.h>
-#include <ripple/resource/Charge.h>
-#include <ripple/resource/Consumer.h>
 #include <ripple/resource/Fees.h>
-#include <ripple/rpc/Context.h>
-#include <ripple/rpc/RPCHandler.h>
-#include <ripple/shamap/Family.h>
-#include <ripple/crypto/csprng.h>
 #include <ripple/beast/asio/io_latency_probe.h>
 #include <ripple/beast/core/LexicalCast.h>
-#include <beast/core/detail/ci_char_traits.hpp>
-#include <boost/asio/signal_set.hpp>
-#include <boost/optional.hpp>
-#include <atomic>
-#include <chrono>
-#include <fstream>
 
 namespace ripple {
 
@@ -325,22 +294,22 @@ class ApplicationImp
 
     NodeStoreScheduler m_nodeStoreScheduler;
     std::unique_ptr <SHAMapStore> m_shaMapStore;
-    std::unique_ptr <NodeStore::Database> m_nodeStore;
     PendingSaves pendingSaves_;
     AccountIDCache accountIDCache_;
     boost::optional<OpenLedger> openLedger_;
 
     // These are not Stoppable-derived
     NodeCache m_tempNodeCache;
     std::unique_ptr <CollectorManager> m_collectorManager;
-    detail::AppFamily family_;
     CachedSLEs cachedSLEs_;
     std::pair<PublicKey, SecretKey> nodeIdentity_;
 
     std::unique_ptr <Resource::Manager> m_resourceManager;
 
     // These are Stoppable-related
     std::unique_ptr <JobQueue> m_jobQueue;
+    std::unique_ptr <NodeStore::Database> m_nodeStore;
+    detail::AppFamily family_;
     // VFALCO TODO Make OrderBookDB abstract
     OrderBookDB m_orderBookDB;
     std::unique_ptr <PathRequests> m_pathRequests;
@@ -416,8 +385,6 @@ class ApplicationImp
             logs_->journal ("SHAMapStore"), logs_->journal ("NodeObject"),
             m_txMaster, *config_))
 
-        , m_nodeStore (m_shaMapStore->makeDatabase ("NodeStore.main", 4))
-
         , accountIDCache_(128000)
 
         , m_tempNodeCache ("NodeCache", 16384, 90, stopwatch(),
@@ -426,8 +393,6 @@ class ApplicationImp
         , m_collectorManager (CollectorManager::New (
             config_->section (SECTION_INSIGHT), logs_->journal("Collector")))
 
-        , family_ (*this, *m_nodeStore, *m_collectorManager)
-
         , cachedSLEs_ (std::chrono::minutes(1), stopwatch())
 
         , m_resourceManager (Resource::make_Manager (
@@ -443,6 +408,10 @@ class ApplicationImp
         //
         // Anything which calls addJob must be a descendant of the JobQueue
         //
+        , m_nodeStore (
+            m_shaMapStore->makeDatabase ("NodeStore.main", 4, *m_jobQueue))
+
+        , family_ (*this, *m_nodeStore, *m_collectorManager)
 
         , m_orderBookDB (*this, *m_jobQueue)
 
@@ -1964,9 +1933,9 @@ bool ApplicationImp::updateTables ()
         auto j = logs_->journal("NodeObject");
         NodeStore::DummyScheduler scheduler;
         std::unique_ptr <NodeStore::Database> source =
-            NodeStore::Manager::instance().make_Database ("NodeStore.import", scheduler,
-                j, 0,
-                config_->section(ConfigSection::importNodeDatabase ()));
+            NodeStore::Manager::instance().make_Database ("NodeStore.import",
+                scheduler, 0, *m_jobQueue,
+                config_->section(ConfigSection::importNodeDatabase ()), j);
 
         JLOG (j.warn())
             << "Node import from '" << source->getName () << "' to '"
```

### src/ripple/app/misc/SHAMapStore.h
```diff
@@ -21,9 +21,7 @@
 #define RIPPLE_APP_MISC_SHAMAPSTORE_H_INCLUDED
 
 #include <ripple/app/ledger/Ledger.h>
-#include <ripple/core/Config.h>
 #include <ripple/nodestore/Manager.h>
-#include <ripple/nodestore/Scheduler.h>
 #include <ripple/protocol/ErrorCodes.h>
 #include <ripple/core/Stoppable.h>
 
@@ -62,7 +60,8 @@ class SHAMapStore
     virtual std::uint32_t clampFetchDepth (std::uint32_t fetch_depth) const = 0;
 
     virtual std::unique_ptr <NodeStore::Database> makeDatabase (
-            std::string const& name, std::int32_t readThreads) = 0;
+            std::string const& name,
+            std::int32_t readThreads, Stoppable& parent) = 0;
 
     /** Highest ledger that may be deleted. */
     virtual LedgerIndex setCanDelete (LedgerIndex canDelete) = 0;
```

### src/ripple/app/misc/SHAMapStoreImp.cpp
```diff
@@ -20,17 +20,10 @@
 #include <BeastConfig.h>
 
 #include <ripple/app/misc/SHAMapStoreImp.h>
-#include <ripple/app/ledger/LedgerMaster.h>
 #include <ripple/app/ledger/TransactionMaster.h>
-#include <ripple/app/main/Application.h>
-#include <ripple/basics/contract.h>
+#include <ripple/app/misc/NetworkOPs.h>
 #include <ripple/core/ConfigSections.h>
 #include <ripple/beast/core/CurrentThreadName.h>
-#include <boost/format.hpp>
-#include <boost/format.hpp>
-#include <boost/optional.hpp>
-#include <memory>
-#include <chrono>
 
 namespace ripple {
 void SHAMapStoreImp::SavedStateDB::init (BasicConfig const& config,
@@ -210,7 +203,7 @@ SHAMapStoreImp::SHAMapStoreImp (
 
 std::unique_ptr <NodeStore::Database>
 SHAMapStoreImp::makeDatabase (std::string const& name,
-        std::int32_t readThreads)
+        std::int32_t readThreads, Stoppable& parent)
 {
     std::unique_ptr <NodeStore::Database> db;
 
@@ -226,8 +219,8 @@ SHAMapStoreImp::makeDatabase (std::string const& name,
         fdlimit_ = writableBackend->fdlimit() + archiveBackend->fdlimit();
 
         std::unique_ptr <NodeStore::DatabaseRotating> dbr =
-                makeDatabaseRotating (name, readThreads, writableBackend,
-                archiveBackend);
+            makeDatabaseRotating (name, readThreads, parent,
+                writableBackend, archiveBackend);
 
         if (!state.writableDb.size())
         {
@@ -242,7 +235,7 @@ SHAMapStoreImp::makeDatabase (std::string const& name,
     else
     {
         db = NodeStore::Manager::instance().make_Database (name, scheduler_,
-            nodeStoreJournal_, readThreads, setup_.nodeDatabase);
+            readThreads, parent, setup_.nodeDatabase, nodeStoreJournal_);
         fdlimit_ = db->fdlimit();
     }
 
@@ -530,12 +523,13 @@ SHAMapStoreImp::makeBackendRotating (std::string path)
 
 std::unique_ptr <NodeStore::DatabaseRotating>
 SHAMapStoreImp::makeDatabaseRotating (std::string const& name,
-        std::int32_t readThreads,
+        std::int32_t readThreads,  Stoppable& parent,
         std::shared_ptr <NodeStore::Backend> writableBackend,
         std::shared_ptr <NodeStore::Backend> archiveBackend) const
 {
-    return NodeStore::Manager::instance().make_DatabaseRotating ("NodeStore.main", scheduler_,
-            readThreads, writableBackend, archiveBackend, nodeStoreJournal_);
+    return NodeStore::Manager::instance().make_DatabaseRotating (
+        name, scheduler_, readThreads, parent,
+        writableBackend, archiveBackend, nodeStoreJournal_);
 }
 
 bool
```

### src/ripple/app/misc/SHAMapStoreImp.h
```diff
@@ -21,18 +21,17 @@
 #define RIPPLE_APP_MISC_SHAMAPSTOREIMP_H_INCLUDED
 
 #include <ripple/app/misc/SHAMapStore.h>
-#include <ripple/app/misc/NetworkOPs.h>
+#include <ripple/app/ledger/LedgerMaster.h>
 #include <ripple/core/DatabaseCon.h>
-#include <ripple/core/SociDB.h>
-#include <ripple/nodestore/impl/Tuning.h>
 #include <ripple/nodestore/DatabaseRotating.h>
-#include <iostream>
 #include <condition_variable>
 #include <thread>
 
 
 namespace ripple {
 
+class NetworkOPs;
+
 class SHAMapStoreImp : public SHAMapStore
 {
 private:
@@ -134,7 +133,8 @@ class SHAMapStoreImp : public SHAMapStore
     }
 
     std::unique_ptr <NodeStore::Database> makeDatabase (
-            std::string const&name, std::int32_t readThreads) override;
+            std::string const&name,
+            std::int32_t readThreads, Stoppable& parent) override;
 
     LedgerIndex
     setCanDelete (LedgerIndex seq) override
@@ -191,7 +191,7 @@ class SHAMapStoreImp : public SHAMapStore
      */
     std::unique_ptr <NodeStore::DatabaseRotating>
     makeDatabaseRotating (std::string const&name,
-            std::int32_t readThreads,
+            std::int32_t readThreads, Stoppable& parent,
             std::shared_ptr <NodeStore::Backend> writableBackend,
             std::shared_ptr <NodeStore::Backend> archiveBackend) const;
 
```

### src/ripple/core/JobQueue.h
```diff
@@ -22,19 +22,12 @@
 
 #include <ripple/basics/LocalValue.h>
 #include <ripple/basics/win32_workaround.h>
-#include <ripple/core/Job.h>
 #include <ripple/core/JobTypes.h>
 #include <ripple/core/JobTypeData.h>
+#include <ripple/core/Stoppable.h>
 #include <ripple/core/impl/Workers.h>
 #include <ripple/json/json_value.h>
-#include <ripple/beast/insight/Collector.h>
-#include <ripple/core/Stoppable.h>
 #include <boost/coroutine/all.hpp>
-#include <boost/function.hpp>
-#include <condition_variable>
-#include <mutex>
-#include <set>
-#include <thread>
 
 namespace ripple {
 
```

### src/ripple/core/Stoppable.h
```diff
@@ -172,11 +172,11 @@ class RootStoppable;
 class Stoppable
 {
 protected:
-    Stoppable (char const* name, RootStoppable& root);
+    Stoppable (std::string name, RootStoppable& root);
 
 public:
     /** Create the Stoppable. */
-    Stoppable (char const* name, Stoppable& parent);
+    Stoppable (std::string name, Stoppable& parent);
 
     /** Destroy the Stoppable. */
     virtual ~Stoppable ();
@@ -294,7 +294,7 @@ class Stoppable
 class RootStoppable : public Stoppable
 {
 public:
-    explicit RootStoppable (char const* name);
+    explicit RootStoppable (std::string name);
 
     ~RootStoppable () = default;
 
@@ -339,7 +339,7 @@ class RootStoppable : public Stoppable
     /*  Notify a root stoppable and children to stop, without waiting.
         Has no effect if the stoppable was already notified.
 
-        Returns true on the first call to stopAsync(), false otherwise.
+        Returns true on the first call to this method, false otherwise.
 
         Thread safety:
             Safe to call from any thread at any time.
```

### src/ripple/core/impl/JobQueue.cpp
```diff
@@ -19,15 +19,7 @@
 
 #include <BeastConfig.h>
 #include <ripple/core/JobQueue.h>
-#include <ripple/core/JobTypes.h>
-#include <ripple/core/JobTypeInfo.h>
-#include <ripple/core/JobTypeData.h>
-#include <ripple/beast/clock/chrono_util.h>
-#include <chrono>
-#include <memory>
-#include <mutex>
-#include <set>
-#include <thread>
+#include <ripple/basics/contract.h>
 
 namespace ripple {
 
@@ -93,6 +85,8 @@ JobQueue::addJob (JobType type, std::string const& name,
     assert (type == jtCLIENT || m_workers.getNumberOfThreads () > 0);
 
     {
+        std::lock_guard <std::mutex> lock (m_mutex);
+
         // If this goes off it means that a child didn't follow
         // the Stoppable API rules. A job may only be added if:
         //
@@ -104,15 +98,10 @@ JobQueue::addJob (JobType type, std::string const& name,
         //          OR
         //      * Not all children are stopped
         //
-        std::lock_guard <std::mutex> lock (m_mutex);
         assert (! isStopped() && (
             m_processCount>0 ||
             ! m_jobSet.empty () ||
             ! areChildrenStopped()));
-    }
-
-    {
-        std::lock_guard <std::mutex> lock (m_mutex);
 
         std::pair <std::set <Job>::iterator, bool> result (
             m_jobSet.insert (Job (type, name, ++m_lastJob,
@@ -218,6 +207,9 @@ void
 JobQueue::addLoadEvents (JobType t, int count,
     std::chrono::milliseconds elapsed)
 {
+    if (isStopped())
+        LogicError ("JobQueue::addLoadEvents() called after JobQueue stopped");
+
     JobDataMap::iterator iter (m_jobData.find (t));
     assert (iter != m_jobData.end ());
     iter->second.load().addSamples (count, elapsed);
```

### src/ripple/core/impl/Stoppable.cpp
```diff
@@ -22,8 +22,8 @@
 
 namespace ripple {
 
-Stoppable::Stoppable (char const* name, RootStoppable& root)
-    : m_name (name)
+Stoppable::Stoppable (std::string name, RootStoppable& root)
+    : m_name (std::move (name))
     , m_root (root)
     , m_child (this)
     , m_started (false)
@@ -32,8 +32,8 @@ Stoppable::Stoppable (char const* name, RootStoppable& root)
 {
 }
 
-Stoppable::Stoppable (char const* name, Stoppable& parent)
-    : m_name (name)
+Stoppable::Stoppable (std::string name, Stoppable& parent)
+    : m_name (std::move (name))
     , m_root (parent.m_root)
     , m_child (this)
     , m_started (false)
@@ -157,8 +157,8 @@ void Stoppable::stopRecursive (beast::Journal j)
 
 //------------------------------------------------------------------------------
 
-RootStoppable::RootStoppable (char const* name)
-    : Stoppable (name, *this)
+RootStoppable::RootStoppable (std::string name)
+    : Stoppable (std::move (name), *this)
     , m_prepared (false)
     , m_calledStop (false)
 {
```

### src/ripple/nodestore/Database.h
```diff
@@ -20,9 +20,10 @@
 #ifndef RIPPLE_NODESTORE_DATABASE_H_INCLUDED
 #define RIPPLE_NODESTORE_DATABASE_H_INCLUDED
 
+#include <ripple/basics/TaggedCache.h>
+#include <ripple/core/Stoppable.h>
 #include <ripple/nodestore/NodeObject.h>
 #include <ripple/nodestore/Backend.h>
-#include <ripple/basics/TaggedCache.h>
 
 namespace ripple {
 namespace NodeStore {
@@ -40,9 +41,20 @@ namespace NodeStore {
 
     @see NodeObject
 */
-class Database
+class Database : public Stoppable
 {
 public:
+    Database() = delete;
+
+    /** Construct the node store.
+
+        @param name The Stoppable name for this Database.
+        @param parent The parent Stoppable.
+    */
+    Database (std::string name, Stoppable& parent)
+        : Stoppable (std::move (name), parent)
+    { }
+
     /** Destroy the node store.
         All pending operations are completed, pending writes flushed,
         and files closed before this returns.
@@ -55,11 +67,6 @@ class Database
     */
     virtual std::string getName () const = 0;
 
-    /** Close the database.
-        This allows the caller to catch exceptions.
-    */
-    virtual void close() = 0;
-
     /** Fetch an object.
         If the object is known to be not in the database, isn't found in the
         database during the fetch, or failed to load correctly during the fetch,
```

### src/ripple/nodestore/Manager.h
```diff
@@ -22,9 +22,6 @@
 
 #include <ripple/nodestore/Factory.h>
 #include <ripple/nodestore/DatabaseRotating.h>
-#include <ripple/basics/BasicConfig.h>
-#include <ripple/basics/Log.h>
-#include <ripple/beast/utility/Journal.h>
 
 namespace ripple {
 namespace NodeStore {
@@ -87,16 +84,18 @@ class Manager
     virtual
     std::unique_ptr <Database>
     make_Database (std::string const& name, Scheduler& scheduler,
-        beast::Journal journal, int readThreads,
-            Section const& backendParameters) = 0;
+        int readThreads, Stoppable& parent,
+            Section const& backendParameters,
+                beast::Journal journal) = 0;
 
     virtual
     std::unique_ptr <DatabaseRotating>
     make_DatabaseRotating (std::string const& name,
         Scheduler& scheduler, std::int32_t readThreads,
-            std::shared_ptr <Backend> writableBackend,
-                std::shared_ptr <Backend> archiveBackend,
-                    beast::Journal journal) = 0;
+            Stoppable& parent,
+                std::shared_ptr <Backend> writableBackend,
+                    std::shared_ptr <Backend> archiveBackend,
+                        beast::Journal journal) = 0;
 };
 
 //------------------------------------------------------------------------------
```

### src/ripple/nodestore/impl/DatabaseImp.h
```diff
@@ -24,16 +24,8 @@
 #include <ripple/nodestore/Scheduler.h>
 #include <ripple/nodestore/impl/Tuning.h>
 #include <ripple/basics/KeyCache.h>
-#include <ripple/basics/Log.h>
 #include <ripple/basics/chrono.h>
-#include <ripple/protocol/digest.h>
-#include <ripple/basics/Slice.h>
-#include <ripple/basics/TaggedCache.h>
 #include <ripple/beast/core/CurrentThreadName.h>
-#include <chrono>
-#include <condition_variable>
-#include <set>
-#include <thread>
 
 namespace ripple {
 namespace NodeStore {
@@ -62,14 +54,21 @@ class DatabaseImp
     bool                      m_readShut;
     uint64_t                  m_readGen;        // current read generation
     int                       fdlimit_;
+    std::atomic <std::uint32_t> m_storeCount;
+    std::atomic <std::uint32_t> m_fetchTotalCount;
+    std::atomic <std::uint32_t> m_fetchHitCount;
+    std::atomic <std::uint32_t> m_storeSize;
+    std::atomic <std::uint32_t> m_fetchSize;
 
 public:
     DatabaseImp (std::string const& name,
                  Scheduler& scheduler,
                  int readThreads,
+                 Stoppable& parent,
                  std::unique_ptr <Backend> backend,
                  beast::Journal journal)
-        : m_journal (journal)
+        : Database (name, parent)
+        , m_journal (journal)
         , m_scheduler (scheduler)
         , m_backend (std::move (backend))
         , m_cache ("NodeStore", cacheTargetSize, cacheTargetSeconds,
@@ -109,16 +108,6 @@ class DatabaseImp
         return m_backend->getName ();
     }
 
-    void
-    close() override
-    {
-        if (m_backend)
-        {
-            m_backend->close();
-            m_backend = nullptr;
-        }
-    }
-
     //------------------------------------------------------------------------------
 
     bool asyncFetch (uint256 const& hash, std::shared_ptr<NodeObject>& object) override
@@ -440,6 +429,18 @@ class DatabaseImp
         return fdlimit_;
     }
 
+    //--------------------------------------------------------------------------
+    //
+    // Stoppable.
+
+    void onStop () override
+    {
+        // After stop time we can no longer use the JobQueue for background
+        // reads.  Join the background read threads.
+        DatabaseImp::stopThreads();
+        stopped();
+    }
+
 protected:
     void stopThreads ()
     {
@@ -456,13 +457,6 @@ class DatabaseImp
         for (auto& e : m_readThreads)
             e.join();
     }
-
-private:
-    std::atomic <std::uint32_t> m_storeCount;
-    std::atomic <std::uint32_t> m_fetchTotalCount;
-    std::atomic <std::uint32_t> m_fetchHitCount;
-    std::atomic <std::uint32_t> m_storeSize;
-    std::atomic <std::uint32_t> m_fetchSize;
 };
 
 }
```

### src/ripple/nodestore/impl/DatabaseRotatingImp.h
```diff
@@ -50,13 +50,15 @@ class DatabaseRotatingImp
     DatabaseRotatingImp (std::string const& name,
                  Scheduler& scheduler,
                  int readThreads,
+                 Stoppable& parent,
                  std::shared_ptr <Backend> writableBackend,
                  std::shared_ptr <Backend> archiveBackend,
                  beast::Journal journal)
             : DatabaseImp (
                 name,
                 scheduler,
                 readThreads,
+                parent,
                 std::unique_ptr <Backend>(),
                 journal)
             , writableBackend_ (writableBackend)
@@ -93,13 +95,6 @@ class DatabaseRotatingImp
         return getWritableBackend()->getName();
     }
 
-    void
-    close() override
-    {
-        // VFALCO TODO How do we close everything?
-        assert(false);
-    }
-
     std::int32_t getWriteLoad() const override
     {
         return getWritableBackend()->getWriteLoad();
```
