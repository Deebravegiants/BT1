# [?] Removing 32bit compatibility cruft.  The resizing functions have always been problematic because they force us to be conservative with transaction siz

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-11-02
Source: https://github.com/nanocurrency/nano-node/commit/bf232a0f61ad486537a2af60f89bd870c399cca5
Type: security-commit

## Details
Removing 32bit compatibility cruft.  The resizing functions have always been problematic because they force us to be conservative with transaction sizes to avoid overflowing.

## Patch
### rai/node/node.cpp
```diff
@@ -1309,14 +1309,6 @@ vote_processor (*this),
 warmed_up (0),
 block_processor (*this)
 {
-	store.environment.sizing_action = [this] ()
-	{
-		auto this_l (shared_from_this ());
-		background ([this_l] ()
-		{
-			this_l->store.environment.handle_environment_sizing ();
-		});
-	};
 	wallets.observer = [this] (rai::account const & account_a, bool active)
 	{
 		observers.wallet (account_a, active);
```

### rai/utility.cpp
```diff
@@ -52,11 +52,7 @@ bool rai::from_string_hex (std::string const & value_a, uint64_t & target_a)
     return result;
 }
 
-rai::mdb_env::mdb_env (bool & error_a, boost::filesystem::path const & path_a) :
-open_transactions (0),
-transaction_iteration (0),
-resizing (false),
-sizing_action ([this] () { handle_environment_sizing (); })
+rai::mdb_env::mdb_env (bool & error_a, boost::filesystem::path const & path_a)
 {
 	boost::system::error_code error;
 	if (path_a.has_parent_path ())
@@ -68,7 +64,7 @@ sizing_action ([this] () { handle_environment_sizing (); })
 			assert (status1 == 0);
 			auto status2 (mdb_env_set_maxdbs (environment, 128));
 			assert (status2 == 0);
-			auto status3 (mdb_env_set_mapsize (environment, 0));
+			auto status3 (mdb_env_set_mapsize (environment, 1ULL * 1024 * 1024 * 1024 * 1024)); // 1 Terabyte
 			assert (status3 == 0);
 			auto status4 (mdb_env_open (environment, path_a.string ().c_str (), MDB_NOSUBDIR, 00600));
 			error_a = status4 != 0;
@@ -99,57 +95,6 @@ rai::mdb_env::operator MDB_env * () const
 	return environment;
 }
 
-void rai::mdb_env::add_transaction ()
-{
-	// Minimize I/O from checking if we need to resive
-	// Too high and the enviroment might overflow
-	// Too low and we're making lots of trips to the disk
-	if ((transaction_iteration++ % rai::database_check_interval) == 0)
-	{
-		sizing_action ();
-	}
-	std::unique_lock <std::mutex> lock_l (lock);
-	// Wait for any resizing operations to complete
-	while (resizing)
-	{
-		resize_notify.wait (lock_l);
-	}
-	++open_transactions;
-}
-
-void rai::mdb_env::handle_environment_sizing ()
-{
-	if (!resizing.exchange (true))
-	{
-		MDB_stat stats;
-		mdb_env_stat (environment, &stats);
-		MDB_envinfo info;
-		mdb_env_info (environment, &info);
-		double used_space (info.me_last_pgno * stats.ms_psize);
-		double needed_space (used_space * 1.25);
-		size_t increments_needed ((needed_space / database_size_increment) + 1);
-		size_t environment_size (increments_needed * database_size_increment);
-		if (info.me_mapsize < environment_size)
-		{
-				std::unique_lock <std::mutex> lock_l (lock);
-				while (open_transactions > 0)
-				{
-					open_notify.wait (lock_l);
-				}
-				mdb_env_set_mapsize (environment, environment_size);
-		}
-		resizing = false;
-		resize_notify.notify_all ();
-	}
-}
-
-void rai::mdb_env::remove_transaction ()
-{
-	std::lock_guard <std::mutex> lock_l (lock);
-	--open_transactions;
-	open_notify.notify_all ();
-}
-
 rai::mdb_val::mdb_val (size_t size_a, void * data_a) :
 value ({size_a, data_a})
 {
@@ -169,15 +114,13 @@ rai::mdb_val::operator MDB_val const & () const
 rai::transaction::transaction (rai::mdb_env & environment_a, MDB_txn * parent_a, bool write) :
 environment (environment_a)
 {
-	environment_a.add_transaction ();
 	auto status (mdb_txn_begin (environment_a, parent_a, write ? 0 : MDB_RDONLY, &handle));
 	assert (status == 0);
 }
 
 rai::transaction::~transaction ()
 {
 	auto status (mdb_txn_commit (handle));
-	environment.remove_transaction ();
 	assert (status == 0);
 }
 
```

### rai/utility.hpp
```diff
@@ -139,17 +139,7 @@ class mdb_env
 	mdb_env (bool &, boost::filesystem::path const &);
 	~mdb_env ();
 	operator MDB_env * () const;
-	void add_transaction ();
-	void remove_transaction ();
-	void handle_environment_sizing ();
 	MDB_env * environment;
-	std::mutex lock;
-	std::condition_variable open_notify;
-	unsigned open_transactions;
-	std::atomic_uint transaction_iteration;
-	std::condition_variable resize_notify;
-	std::atomic_bool resizing;
-	std::function <void ()> sizing_action;
 };
 class mdb_val
 {
```
