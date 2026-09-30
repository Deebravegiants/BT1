# [?] miner: fix double free of thread attributes

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-06-09
Source: https://github.com/monero-project/monero/commit/f2f207d63578735c875472cf56ad4dee787ba110
Type: security-commit

## Details
miner: fix double free of thread attributes

issue: #5568

## Patch
### src/cryptonote_basic/miner.cpp
```diff
@@ -123,7 +123,7 @@ namespace cryptonote
     m_miner_extra_sleep(BACKGROUND_MINING_DEFAULT_MINER_EXTRA_SLEEP_MILLIS),
     m_block_reward(0)
   {
-
+    m_attrs.set_stack_size(THREAD_STACK_SIZE);
   }
   //-----------------------------------------------------------------------------------------------------
   miner::~miner()
@@ -360,7 +360,7 @@ namespace cryptonote
     return m_threads_total;
   }
   //-----------------------------------------------------------------------------------------------------
-  bool miner::start(const account_public_address& adr, size_t threads_count, const boost::thread::attributes& attrs, bool do_background, bool ignore_battery)
+  bool miner::start(const account_public_address& adr, size_t threads_count, bool do_background, bool ignore_battery)
   {
     m_block_reward = 0;
     m_mine_address = adr;
@@ -371,7 +371,6 @@ namespace cryptonote
       m_threads_autodetect.push_back({epee::misc_utils::get_ns_count(), m_total_hashes});
       m_threads_total = 1;
     }
-    m_attrs = attrs;
     m_starter_nonce = crypto::rand<uint32_t>();
     CRITICAL_REGION_LOCAL(m_threads_lock);
     if(is_mining())
@@ -395,7 +394,7 @@ namespace cryptonote
     
     for(size_t i = 0; i != m_threads_total; i++)
     {
-      m_threads.push_back(boost::thread(attrs, boost::bind(&miner::worker_thread, this)));
+      m_threads.push_back(boost::thread(m_attrs, boost::bind(&miner::worker_thread, this)));
     }
 
     if (threads_count == 0)
@@ -405,7 +404,7 @@ namespace cryptonote
 
     if( get_is_background_mining_enabled() )
     {
-      m_background_mining_thread = boost::thread(attrs, boost::bind(&miner::background_worker_thread, this));
+      m_background_mining_thread = boost::thread(m_attrs, boost::bind(&miner::background_worker_thread, this));
       LOG_PRINT_L0("Background mining controller thread started" );
     }
 
@@ -487,10 +486,7 @@ namespace cryptonote
   {
     if(m_do_mining)
     {
-      boost::thread::attributes attrs;
-      attrs.set_stack_size(THREAD_STACK_SIZE);
-
-      start(m_mine_address, m_threads_total, attrs, get_is_background_mining_enabled(), get_ignore_battery());
+      start(m_mine_address, m_threads_total, get_is_background_mining_enabled(), get_ignore_battery());
     }
   }
   //-----------------------------------------------------------------------------------------------------
```

### src/cryptonote_basic/miner.h
```diff
@@ -64,7 +64,7 @@ namespace cryptonote
     static void init_options(boost::program_options::options_description& desc);
     bool set_block_template(const block& bl, const difficulty_type& diffic, uint64_t height, uint64_t block_reward);
     bool on_block_chain_update();
-    bool start(const account_public_address& adr, size_t threads_count, const boost::thread::attributes& attrs, bool do_background = false, bool ignore_battery = false);
+    bool start(const account_public_address& adr, size_t threads_count, bool do_background = false, bool ignore_battery = false);
     uint64_t get_speed() const;
     uint32_t get_threads_count() const;
     void send_stop_signal();
```

### src/rpc/core_rpc_server.cpp
```diff
@@ -905,16 +905,13 @@ namespace cryptonote
       return true;
     }
 
-    boost::thread::attributes attrs;
-    attrs.set_stack_size(THREAD_STACK_SIZE);
-
     cryptonote::miner &miner= m_core.get_miner();
     if (miner.is_mining())
     {
       res.status = "Already mining";
       return true;
     }
-    if(!miner.start(info.address, static_cast<size_t>(req.threads_count), attrs, req.do_background_mining, req.ignore_battery))
+    if(!miner.start(info.address, static_cast<size_t>(req.threads_count), req.do_background_mining, req.ignore_battery))
     {
       res.status = "Failed, mining not started";
       LOG_PRINT_L0(res.status);
```

### src/rpc/daemon_handler.cpp
```diff
@@ -408,10 +408,7 @@ namespace rpc
       return;
     }
 
-    boost::thread::attributes attrs;
-    attrs.set_stack_size(THREAD_STACK_SIZE);
-
-    if(!m_core.get_miner().start(info.address, static_cast<size_t>(req.threads_count), attrs, req.do_background_mining, req.ignore_battery))
+    if(!m_core.get_miner().start(info.address, static_cast<size_t>(req.threads_count), req.do_background_mining, req.ignore_battery))
     {
       res.error_details = "Failed, mining not started";
       LOG_PRINT_L0(res.error_details);
```
