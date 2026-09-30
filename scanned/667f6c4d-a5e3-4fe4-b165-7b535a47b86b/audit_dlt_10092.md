# [?] Fix wallet race condition

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-01-08
Source: https://github.com/nanocurrency/nano-node/commit/e52556acc5f17e32b587fc2a52989e334c87b0ce
Type: security-commit

## Details
Fix wallet race condition

Also give fork_bootstrap_flip a little more margin, it is unstable with the current iteration count

## Patch
### rai/core_test/node.cpp
```diff
@@ -939,7 +939,7 @@ TEST (node, fork_bootstrap_flip)
 		system0.poll ();
 		system1.poll ();
 		++iterations2;
-		ASSERT_LT (iterations2, 200);
+		ASSERT_LT (iterations2, 1000);
 		rai::transaction transaction (node2.store.environment, nullptr, false);
 		again = !node2.store.block_exists (transaction, send1->hash ());
 	}
```

### rai/core_test/wallet.cpp
```diff
@@ -889,20 +889,92 @@ TEST (wallet, password_race)
 	rai::thread_runner runner (system.service, system.nodes[0]->config.io_threads);
 	auto wallet = system.wallet (0);
 	system.nodes[0]->background ([&wallet]() {
-		for (int i = 0; i < 100; i++) {
+		for (int i = 0; i < 100; i++)
+		{
 			rai::transaction transaction (wallet->store.environment, nullptr, true);
-			wallet->store.rekey (transaction, std::to_string(i));
+			wallet->store.rekey (transaction, std::to_string (i));
 		}
 	});
-	for (int i = 0; i < 100; i++) {
+	for (int i = 0; i < 100; i++)
+	{
 		rai::transaction transaction (wallet->store.environment, nullptr, false);
 		// Password should always be valid, the rekey operation should be atomic.
 		bool ok = wallet->store.valid_password (transaction);
 		EXPECT_TRUE (ok);
-		if (!ok) {
+		if (!ok)
+		{
 			break;
 		}
 	}
 	system.stop ();
 	runner.join ();
-}
\ No newline at end of file
+}
+
+TEST (wallet, password_race_corrupt_seed)
+{
+	rai::system system (24000, 1);
+	rai::thread_runner runner (system.service, system.nodes[0]->config.io_threads);
+	auto wallet = system.wallet (0);
+	rai::raw_key seed;
+	{
+		rai::transaction transaction (wallet->store.environment, nullptr, true);
+		ASSERT_FALSE (wallet->store.rekey (transaction, "4567"));
+		wallet->store.seed (seed, transaction);
+	}
+	{
+		rai::transaction transaction (wallet->store.environment, nullptr, false);
+		ASSERT_FALSE (wallet->store.attempt_password (transaction, "4567"));
+	}
+	for (int i = 0; i < 100; i++)
+	{
+		system.nodes[0]->background ([&wallet]() {
+			for (int i = 0; i < 10; i++)
+			{
+				rai::transaction transaction (wallet->store.environment, nullptr, true);
+				wallet->store.rekey (transaction, "0000");
+			}
+		});
+		system.nodes[0]->background ([&wallet]() {
+			for (int i = 0; i < 10; i++)
+			{
+				rai::transaction transaction (wallet->store.environment, nullptr, true);
+				wallet->store.rekey (transaction, "1234");
+			}
+		});
+		system.nodes[0]->background ([&wallet]() {
+			for (int i = 0; i < 10; i++)
+			{
+				rai::transaction transaction (wallet->store.environment, nullptr, false);
+				wallet->store.attempt_password (transaction, "1234");
+			}
+		});
+	}
+	system.stop ();
+	runner.join ();
+	{
+		rai::transaction transaction (wallet->store.environment, nullptr, true);
+		bool ok = false;
+		if (!wallet->store.attempt_password (transaction, "1234"))
+		{
+			rai::raw_key seed_now;
+			wallet->store.seed (seed_now, transaction);
+			ASSERT_TRUE (seed_now == seed);
+		}
+		else if (!wallet->store.attempt_password (transaction, "0000"))
+		{
+			rai::raw_key seed_now;
+			wallet->store.seed (seed_now, transaction);
+			ASSERT_TRUE (seed_now == seed);
+		}
+		else if (!wallet->store.attempt_password (transaction, "4567"))
+		{
+			rai::raw_key seed_now;
+			wallet->store.seed (seed_now, transaction);
+			ASSERT_TRUE (seed_now == seed);
+		}
+		else
+		{
+			ASSERT_FALSE (true);
+		}
+	}
+}
```

### rai/lib/blocks.cpp
```diff
@@ -20,7 +20,7 @@ bool rai::from_string_hex (std::string const & value_a, uint64_t & target_a)
 			stream << std::hex << std::noshowbase;
 			try
 			{
-                		uint64_t number_l;
+				uint64_t number_l;
 				stream >> number_l;
 				target_a = number_l;
 				if (!stream.eof ())
```

### rai/node/node.cpp
```diff
@@ -1343,7 +1343,7 @@ warmed_up (0),
 block_processor (*this),
 block_processor_thread ([this]() { this->block_processor.process_blocks (); })
 {
-	wallets.observer = [this] (bool active) {
+	wallets.observer = [this](bool active) {
 		observers.wallet (active);
 	};
 	peers.peer_observer = [this](rai::endpoint const & endpoint_a) {
@@ -2777,9 +2777,9 @@ void rai::active_transactions::announce_votes ()
 	std::vector<rai::block_hash> inactive;
 	rai::transaction transaction (node.store.environment, nullptr, true);
 	std::lock_guard<std::mutex> lock (mutex);
-	
+
 	{
-        	size_t announcements (0);
+		size_t announcements (0);
 		auto i (roots.begin ());
 		auto n (roots.end ());
 		// Announce our decision for up to `announcements_per_interval' conflicts
```

### rai/node/wallet.cpp
```diff
@@ -27,10 +27,12 @@ rai::uint256_union rai::wallet_store::salt (MDB_txn * transaction_a)
 
 void rai::wallet_store::wallet_key (rai::raw_key & prv_a, MDB_txn * transaction_a)
 {
-	rai::wallet_value value (entry_get_raw (transaction_a, rai::wallet_store::wallet_key_special));
+	std::lock_guard<std::recursive_mutex> lock (mutex);
+	rai::raw_key wallet_l;
+	wallet_key_mem.value (wallet_l);
 	rai::raw_key password_l;
 	password.value (password_l);
-	prv_a.decrypt (value.key, password_l, salt (transaction_a).owords[0]);
+	prv_a.decrypt (wallet_l.data, password_l, salt (transaction_a).owords[0]);
 }
 
 void rai::wallet_store::seed (rai::raw_key & prv_a, MDB_txn * transaction_a)
@@ -126,15 +128,20 @@ bool rai::wallet_store::valid_password (MDB_txn * transaction_a)
 	wallet_key (wallet_key_l, transaction_a);
 	rai::uint256_union check_l;
 	check_l.encrypt (zero, wallet_key_l, salt (transaction_a).owords[0]);
-	return check (transaction_a) == check_l;
+	bool ok = check (transaction_a) == check_l;
+	return ok;
 }
 
 bool rai::wallet_store::attempt_password (MDB_txn * transaction_a, std::string const & password_a)
 {
-	rai::raw_key password_l;
-	derive_key (password_l, transaction_a, password_a);
-	password.value_set (password_l);
-	auto result (!valid_password (transaction_a));
+	bool result = false;
+	{
+		std::lock_guard<std::recursive_mutex> lock (mutex);
+		rai::raw_key password_l;
+		derive_key (password_l, transaction_a, password_a);
+		password.value_set (password_l);
+		result = !valid_password (transaction_a);
+	}
 	if (!result)
 	{
 		if (version (transaction_a) == version_1)
@@ -151,6 +158,7 @@ bool rai::wallet_store::attempt_password (MDB_txn * transaction_a, std::string c
 
 bool rai::wallet_store::rekey (MDB_txn * transaction_a, std::string const & password_a)
 {
+	std::lock_guard<std::recursive_mutex> lock (mutex);
 	bool result (false);
 	if (valid_password (transaction_a))
 	{
@@ -163,6 +171,9 @@ bool rai::wallet_store::rekey (MDB_txn * transaction_a, std::string const & pass
 		password.value_set (password_new);
 		rai::uint256_union encrypted;
 		encrypted.encrypt (wallet_key_l, password_new, salt (transaction_a).owords[0]);
+		rai::raw_key wallet_enc;
+		wallet_enc.data = encrypted;
+		wallet_key_mem.value_set (wallet_enc);
 		entry_put_raw (transaction_a, rai::wallet_store::wallet_key_special, rai::wallet_value (encrypted, 0));
 	}
 	else
@@ -257,6 +268,7 @@ int const rai::wallet_store::special_count (7);
 
 rai::wallet_store::wallet_store (bool & init_a, rai::kdf & kdf_a, rai::transaction & transaction_a, rai::account representative_a, unsigned fanout_a, std::string const & wallet_a, std::string const & json_a) :
 password (0, fanout_a),
+wallet_key_mem (0, fanout_a),
 kdf (kdf_a),
 environment (transaction_a.environment)
 {
@@ -306,11 +318,14 @@ environment (transaction_a.environment)
 		rai::raw_key key;
 		key.data.clear ();
 		password.value_set (key);
+		key.data = entry_get_raw (transaction_a, rai::wallet_store::wallet_key_special).key;
+		wallet_key_mem.value_set (key);
 	}
 }
 
 rai::wallet_store::wallet_store (bool & init_a, rai::kdf & kdf_a, rai::transaction & transaction_a, rai::account representative_a, unsigned fanout_a, std::string const & wallet_a) :
 password (0, fanout_a),
+wallet_key_mem (0, fanout_a),
 kdf (kdf_a),
 environment (transaction_a.environment)
 {
@@ -339,6 +354,9 @@ environment (transaction_a.environment)
 			rai::uint256_union encrypted;
 			encrypted.encrypt (wallet_key, zero, salt_l.owords[0]);
 			entry_put_raw (transaction_a, rai::wallet_store::wallet_key_special, rai::wallet_value (encrypted, 0));
+			rai::raw_key wallet_key_enc;
+			wallet_key_enc.data = encrypted;
+			wallet_key_mem.value_set (wallet_key_enc);
 			rai::uint256_union check;
 			check.encrypt (zero, wallet_key, salt_l.owords[0]);
 			entry_put_raw (transaction_a, rai::wallet_store::check_special, rai::wallet_value (check, 0));
@@ -349,6 +367,9 @@ environment (transaction_a.environment)
 			entry_put_raw (transaction_a, rai::wallet_store::deterministic_index_special, rai::wallet_value (rai::uint256_union (0), 0));
 		}
 	}
+	rai::raw_key key;
+	key.data = entry_get_raw (transaction_a, rai::wallet_store::wallet_key_special).key;
+	wallet_key_mem.value_set (key);
 }
 
 std::vector<rai::account> rai::wallet_store::accounts (MDB_txn * transaction_a)
@@ -689,13 +710,14 @@ node (node_a)
 
 void rai::wallet::enter_initial_password ()
 {
+	rai::transaction transaction (store.environment, nullptr, true);
+	std::lock_guard<std::recursive_mutex> lock (store.mutex);
 	rai::raw_key password_l;
 	store.password.value (password_l);
 	if (password_l.data.is_zero ())
 	{
 		if (valid_password ())
 		{
-			rai::transaction transaction (store.environment, nullptr, true);
 			// Newly created wallets have a zero key
 			store.rekey (transaction, "");
 		}
@@ -1202,7 +1224,7 @@ rai::wallets::wallets (bool & error_a, rai::node & node_a) :
 observer ([](bool) {}),
 node (node_a),
 stopped (false),
-thread ([this] () { do_wallet_actions (); })
+thread ([this]() { do_wallet_actions (); })
 {
 	if (!error_a)
 	{
@@ -1303,7 +1325,7 @@ void rai::wallets::destroy (rai::uint256_union const & id_a)
 
 void rai::wallets::do_wallet_actions ()
 {
-	std::unique_lock <std::mutex> lock (mutex);
+	std::unique_lock<std::mutex> lock (mutex);
 	while (!stopped)
 	{
 		if (!actions.empty ())
@@ -1326,7 +1348,7 @@ void rai::wallets::do_wallet_actions ()
 
 void rai::wallets::queue_wallet_action (rai::uint128_t const & amount_a, std::function<void()> const & action_a)
 {
-	std::lock_guard <std::mutex> lock (mutex);
+	std::lock_guard<std::mutex> lock (mutex);
 	actions.insert (std::make_pair (amount_a, std::move (action_a)));
 	condition.notify_all ();
 }
@@ -1374,7 +1396,7 @@ bool rai::wallets::exists (MDB_txn * transaction_a, rai::public_key const & acco
 
 void rai::wallets::stop ()
 {
-	std::lock_guard <std::mutex> lock (mutex);
+	std::lock_guard<std::mutex> lock (mutex);
 	stopped = true;
 	condition.notify_all ();
 }
```

### rai/node/wallet.hpp
```diff
@@ -95,6 +95,7 @@ class wallet_store
 	void upgrade_v1_v2 ();
 	void upgrade_v2_v3 ();
 	rai::fan password;
+	rai::fan wallet_key_mem;
 	static unsigned const version_1;
 	static unsigned const version_2;
 	static unsigned const version_3;
@@ -113,6 +114,7 @@ class wallet_store
 	rai::kdf & kdf;
 	rai::mdb_env & environment;
 	MDB_dbi handle;
+	std::recursive_mutex mutex;
 };
 class node;
 // A wallet is a set of account keys encrypted by a common encryption key
```
