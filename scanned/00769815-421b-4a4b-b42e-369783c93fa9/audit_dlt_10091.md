# [?] Fix wallet creation crash, add lmdb_max_dbs config

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-01-11
Source: https://github.com/nanocurrency/nano-node/commit/8145ae1e6746b27822ba86903fb026c62a9f4792
Type: security-commit

## Details
Fix wallet creation crash, add lmdb_max_dbs config

## Patch
### rai/core_test/node.cpp
```diff
@@ -494,6 +494,7 @@ TEST (node_config, serialization)
 	config1.callback_address = "test";
 	config1.callback_port = 10;
 	config1.callback_target = "test";
+	config1.lmdb_max_dbs = 256;
 	boost::property_tree::ptree tree;
 	config1.serialize_json (tree);
 	rai::logging logging2;
@@ -522,6 +523,7 @@ TEST (node_config, serialization)
 	ASSERT_EQ (config2.callback_address, config1.callback_address);
 	ASSERT_EQ (config2.callback_port, config1.callback_port);
 	ASSERT_EQ (config2.callback_target, config1.callback_target);
+	ASSERT_EQ (config2.lmdb_max_dbs, config1.lmdb_max_dbs);
 }
 
 TEST (node_config, v1_v2_upgrade)
```

### rai/core_test/rpc.cpp
```diff
@@ -3066,3 +3066,25 @@ TEST (rpc, wallet_locked)
 	std::string account_text1 (response.json.get<std::string> ("locked"));
 	ASSERT_EQ (account_text1, "0");
 }
+
+TEST (rpc, wallet_create_fail)
+{
+	rai::system system (24000, 1);
+	rai::rpc rpc (system.service, *system.nodes[0], rai::rpc_config (true));
+	auto node = system.nodes[0];
+	// lmdb_max_dbs should be removed once the wallet store is refactored to support more wallets.
+	for (int i = 0; i < 113; i++)
+	{
+		rai::keypair key;
+		node->wallets.create (key.pub);
+	}
+	rpc.start ();
+	boost::property_tree::ptree request;
+	request.put ("action", "wallet_create");
+	test_response response (request, rpc, system.service);
+	while (response.status == 0)
+	{
+		system.poll ();
+	}
+	ASSERT_EQ ("Failed to create wallet. Increase lmdb_max_dbs in node config.", response.json.get<std::string> ("error"));
+}
\ No newline at end of file
```

### rai/core_test/wallets.cpp
```diff
@@ -69,4 +69,27 @@ TEST (wallets, remove)
 		ASSERT_FALSE (error);
 		ASSERT_EQ (1, wallets.items.size ());
 	}
-}
\ No newline at end of file
+}
+
+TEST (wallets, wallet_create_max)
+{
+	rai::system system (24000, 1);
+	bool error (false);
+	rai::wallets wallets (error, *system.nodes[0]);
+	// lmdb_max_dbs should be removed once the wallet store is refactored to support more wallets.
+	for (int i = 0; i < 113; i++)
+	{
+		rai::keypair key;
+		auto wallet = wallets.create (key.pub);
+		auto existing = wallets.items.find (key.pub);
+		ASSERT_TRUE (existing != wallets.items.end ());
+		rai::raw_key seed;
+		seed.data = 0;
+		rai::transaction transaction (system.nodes[0]->store.environment, nullptr, true);
+		existing->second->store.seed_set (transaction, seed);
+	}
+	rai::keypair key;
+	wallets.create (key.pub);
+	auto existing = wallets.items.find (key.pub);
+	ASSERT_TRUE (existing == wallets.items.end ());
+}
```

### rai/node/node.cpp
```diff
@@ -747,7 +747,8 @@ io_threads (std::max<unsigned> (4, std::thread::hardware_concurrency ())),
 work_threads (std::max<unsigned> (4, std::thread::hardware_concurrency ())),
 enable_voting (true),
 bootstrap_connections (4),
-callback_port (0)
+callback_port (0),
+lmdb_max_dbs (128)
 {
 	switch (rai::rai_network)
 	{
@@ -780,7 +781,7 @@ callback_port (0)
 
 void rai::node_config::serialize_json (boost::property_tree::ptree & tree_a) const
 {
-	tree_a.put ("version", "7");
+	tree_a.put ("version", "8");
 	tree_a.put ("peering_port", std::to_string (peering_port));
 	tree_a.put ("bootstrap_fraction_numerator", std::to_string (bootstrap_fraction_numerator));
 	tree_a.put ("receive_minimum", receive_minimum.to_string_dec ());
@@ -820,6 +821,7 @@ void rai::node_config::serialize_json (boost::property_tree::ptree & tree_a) con
 	tree_a.put ("callback_address", callback_address);
 	tree_a.put ("callback_port", std::to_string (callback_port));
 	tree_a.put ("callback_target", callback_target);
+	tree_a.put ("lmdb_max_dbs", lmdb_max_dbs);
 }
 
 bool rai::node_config::upgrade_json (unsigned version, boost::property_tree::ptree & tree_a)
@@ -888,6 +890,11 @@ bool rai::node_config::upgrade_json (unsigned version, boost::property_tree::ptr
 			result = true;
 			break;
 		case 7:
+			tree_a.put ("lmdb_max_dbs", "128");
+			tree_a.put ("version", "8");
+			result = true;
+			break;
+		case 8:
 			break;
 		default:
 			throw std::runtime_error ("Unknown node_config version");
@@ -958,6 +965,7 @@ bool rai::node_config::deserialize_json (bool & upgraded_a, boost::property_tree
 		callback_address = tree_a.get<std::string> ("callback_address");
 		auto callback_port_l (tree_a.get<std::string> ("callback_port"));
 		callback_target = tree_a.get<std::string> ("callback_target");
+		auto lmdb_max_dbs_l = tree_a.get<std::string> ("lmdb_max_dbs");
 		result |= parse_port (callback_port_l, callback_port);
 		try
 		{
@@ -967,6 +975,7 @@ bool rai::node_config::deserialize_json (bool & upgraded_a, boost::property_tree
 			io_threads = std::stoul (io_threads_l);
 			work_threads = std::stoul (work_threads_l);
 			bootstrap_connections = std::stoul (bootstrap_connections_l);
+			lmdb_max_dbs = std::stoi (lmdb_max_dbs_l);
 			result |= peering_port > std::numeric_limits<uint16_t>::max ();
 			result |= logging.deserialize_json (upgraded_a, logging_l);
 			result |= receive_minimum.decode_dec (receive_minimum_l);
@@ -1335,7 +1344,7 @@ service (service_a),
 config (config_a),
 alarm (alarm_a),
 work (work_a),
-store (init_a.block_store_init, application_path_a / "data.ldb"),
+store (init_a.block_store_init, application_path_a / "data.ldb", config_a.lmdb_max_dbs),
 gap_cache (*this),
 ledger (store, config_a.inactive_supply.number ()),
 active (*this),
```

### rai/node/node.hpp
```diff
@@ -403,6 +403,7 @@ class node_config
 	std::string callback_address;
 	uint16_t callback_port;
 	std::string callback_target;
+	int lmdb_max_dbs;
 	static std::chrono::seconds constexpr keepalive_period = std::chrono::seconds (60);
 	static std::chrono::seconds constexpr keepalive_cutoff = keepalive_period * 5;
 	static std::chrono::minutes constexpr wallet_backup_interval = std::chrono::minutes (5);
```

### rai/node/rpc.cpp
```diff
@@ -3382,10 +3382,19 @@ void rai::rpc_handler::wallet_create ()
 	if (rpc.config.enable_control)
 	{
 		rai::keypair wallet_id;
-		auto wallet (node.wallets.create (wallet_id.pub));
-		boost::property_tree::ptree response_l;
-		response_l.put ("wallet", wallet_id.pub.to_string ());
-		response (response_l);
+		node.wallets.create (wallet_id.pub);
+		rai::transaction transaction (node.store.environment, nullptr, false);
+		auto existing (node.wallets.items.find (wallet_id.pub));
+		if (existing != node.wallets.items.end ())
+		{
+			boost::property_tree::ptree response_l;
+			response_l.put ("wallet", wallet_id.pub.to_string ());
+			response (response_l);
+		}
+		else
+		{
+			error_response (response, "Failed to create wallet. Increase lmdb_max_dbs in node config.");
+		}
 	}
 	else
 	{
```

### rai/node/utility.cpp
```diff
@@ -12,7 +12,7 @@ boost::filesystem::path rai::unique_path ()
 	return result;
 }
 
-rai::mdb_env::mdb_env (bool & error_a, boost::filesystem::path const & path_a)
+rai::mdb_env::mdb_env (bool & error_a, boost::filesystem::path const & path_a, int max_dbs)
 {
 	boost::system::error_code error;
 	if (path_a.has_parent_path ())
@@ -22,7 +22,7 @@ rai::mdb_env::mdb_env (bool & error_a, boost::filesystem::path const & path_a)
 		{
 			auto status1 (mdb_env_create (&environment));
 			assert (status1 == 0);
-			auto status2 (mdb_env_set_maxdbs (environment, 128));
+			auto status2 (mdb_env_set_maxdbs (environment, max_dbs));
 			assert (status2 == 0);
 			auto status3 (mdb_env_set_mapsize (environment, 1ULL * 1024 * 1024 * 1024 * 1024)); // 1 Terabyte
 			assert (status3 == 0);
```

### rai/node/utility.hpp
```diff
@@ -101,7 +101,7 @@ bool fetch_object (T & object, boost::filesystem::path const & path_a, std::fstr
 class mdb_env
 {
 public:
-	mdb_env (bool &, boost::filesystem::path const &);
+	mdb_env (bool &, boost::filesystem::path const &, int max_dbs = 128);
 	~mdb_env ();
 	operator MDB_env * () const;
 	MDB_env * environment;
```

### rai/node/wallet.cpp
```diff
@@ -1281,10 +1281,10 @@ std::shared_ptr<rai::wallet> rai::wallets::create (rai::uint256_union const & id
 	{
 		rai::transaction transaction (node.store.environment, nullptr, true);
 		result = std::make_shared<rai::wallet> (error, transaction, node, id_a.to_string ());
-		items[id_a] = result;
 	}
 	if (!error)
 	{
+		items[id_a] = result;
 		node.background ([result]() {
 			result->enter_initial_password ();
 		});
```

### rai/secure.cpp
```diff
@@ -453,8 +453,8 @@ size_t rai::block_counts::sum ()
 	return send + receive + open + change;
 }
 
-rai::block_store::block_store (bool & error_a, boost::filesystem::path const & path_a) :
-environment (error_a, path_a),
+rai::block_store::block_store (bool & error_a, boost::filesystem::path const & path_a, int lmdb_max_dbs) :
+environment (error_a, path_a, lmdb_max_dbs),
 frontiers (0),
 accounts (0),
 send_blocks (0),
```

### rai/secure.hpp
```diff
@@ -173,7 +173,7 @@ class vote_result
 class block_store
 {
 public:
-	block_store (bool &, boost::filesystem::path const &);
+	block_store (bool &, boost::filesystem::path const &, int lmdb_max_dbs = 128);
 	uint64_t now ();
 
 	MDB_dbi block_database (rai::block_type);
```
