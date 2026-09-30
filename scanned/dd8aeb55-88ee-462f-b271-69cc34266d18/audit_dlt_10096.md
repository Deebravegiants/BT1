# [?] Fixing rare deadlock in bootstrapping.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-12-14
Source: https://github.com/nanocurrency/nano-node/commit/ac75ae76eda8201e377071c8e8a4897538933625
Type: security-commit

## Details
Fixing rare deadlock in bootstrapping.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -307,46 +307,46 @@ void rai::frontier_req_client::unsynced (MDB_txn * transaction_a, rai::block_has
 
 void rai::frontier_req_client::received_frontier (boost::system::error_code const & ec, size_t size_a)
 {
-    if (!ec)
-    {
-        assert (size_a == sizeof (rai::uint256_union) + sizeof (rai::uint256_union));
-        rai::account account;
-        rai::bufferstream account_stream (connection->receive_buffer.data (), sizeof (rai::uint256_union));
-        auto error1 (rai::read (account_stream, account));
-        assert (!error1);
-        rai::block_hash latest;
-        rai::bufferstream latest_stream (connection->receive_buffer.data () + sizeof (rai::uint256_union), sizeof (rai::uint256_union));
-        auto error2 (rai::read (latest_stream, latest));
-        assert (!error2);
+	if (!ec)
+	{
+		assert (size_a == sizeof (rai::uint256_union) + sizeof (rai::uint256_union));
+		rai::account account;
+		rai::bufferstream account_stream (connection->receive_buffer.data (), sizeof (rai::uint256_union));
+		auto error1 (rai::read (account_stream, account));
+		assert (!error1);
+		rai::block_hash latest;
+		rai::bufferstream latest_stream (connection->receive_buffer.data () + sizeof (rai::uint256_union), sizeof (rai::uint256_union));
+		auto error2 (rai::read (latest_stream, latest));
+		assert (!error2);
 		++count;
 		auto now (std::chrono::system_clock::now ());
 		if (next_report < now)
 		{
 			next_report = now + std::chrono::seconds (15);
 			BOOST_LOG (connection->node->log) << boost::str (boost::format ("Received %1% frontiers from %2%") % std::to_string (count) % connection->socket.remote_endpoint ());
 		}
-        if (!account.is_zero ())
-        {
-            while (!current.is_zero () && current < account)
-            {
+		if (!account.is_zero ())
+		{
+			while (!current.is_zero () && current < account)
+			{
 				// We know about an account they don't.
 				rai::transaction transaction (connection->node->store.environment, nullptr, true);
 				if (connection->node->wallets.exists (transaction, current))
 				{
 					unsynced (transaction, info.head, 0);
 				}
 				next (transaction);
-            }
-            if (!current.is_zero ())
-            {
-                if (account == current)
-                {
+			}
+			if (!current.is_zero ())
+			{
+				if (account == current)
+				{
 					rai::transaction transaction (connection->node->store.environment, nullptr, true);
-                    if (latest == info.head)
-                    {
-                        // In sync
-                    }
-                    else
+					if (latest == info.head)
+					{
+						// In sync
+					}
+					else
 					{
 						if (connection->node->store.block_exists (transaction, latest))
 						{
@@ -370,21 +370,21 @@ void rai::frontier_req_client::received_frontier (boost::system::error_code cons
 						}
 					}
 					next (transaction);
-                }
-                else
-                {
-                    assert (account < current);
-                    request_account (account, latest);
-                }
-            }
-            else
-            {
-                request_account (account, latest);
-            }
-            receive_frontier ();
-        }
-        else
-        {
+				}
+				else
+				{
+					assert (account < current);
+					request_account (account, latest);
+				}
+			}
+			else
+			{
+				request_account (account, latest);
+			}
+			receive_frontier ();
+		}
+		else
+		{
 			{
 				rai::transaction transaction (connection->node->store.environment, nullptr, true);
 				while (!current.is_zero ())
@@ -407,15 +407,15 @@ void rai::frontier_req_client::received_frontier (boost::system::error_code cons
 				}
 				connection->attempt->pool_connection (connection);
 			}
-        }
-    }
-    else
-    {
-        if (connection->node->config.logging.network_logging ())
-        {
-            BOOST_LOG (connection->node->log) << boost::str (boost::format ("Error while receiving frontier %1%") % ec.message ());
-        }
-    }
+		}
+	}
+	else
+	{
+		if (connection->node->config.logging.network_logging ())
+		{
+			BOOST_LOG (connection->node->log) << boost::str (boost::format ("Error while receiving frontier %1%") % ec.message ());
+		}
+	}
 }
 
 void rai::frontier_req_client::next (MDB_txn * transaction_a)
@@ -435,12 +435,12 @@ void rai::frontier_req_client::next (MDB_txn * transaction_a)
 rai::bulk_pull_client::bulk_pull_client (std::shared_ptr <rai::bootstrap_client> connection_a) :
 connection (connection_a)
 {
-    ++connection->attempt->pulling;
+	++connection->attempt->pulling;
 }
 
 rai::bulk_pull_client::~bulk_pull_client ()
 {
-    --connection->attempt->pulling;
+	--connection->attempt->pulling;
 	if (!pull.account.is_zero ())
 	{
 		connection->attempt->requeue_pull (pull);
@@ -809,14 +809,19 @@ bool rai::bootstrap_attempt::request_frontier (std::unique_lock <std::mutex> & l
 
 void rai::bootstrap_attempt::request_pull (std::unique_lock <std::mutex> & lock_a)
 {
-    auto connection_l (connection (lock_a));
-    if (connection_l)
-    {
-        auto pull (pulls.front ());
-        pulls.pop_front ();
-        auto client (std::make_shared <rai::bulk_pull_client> (connection_l));
-        client->request (pull);
-    }
+	auto connection_l (connection (lock_a));
+	if (connection_l)
+	{
+		auto pull (pulls.front ());
+		pulls.pop_front ();
+		auto client (std::make_shared <rai::bulk_pull_client> (connection_l));
+		// The bulk_pull_client destructor attempt to requeue_pull which can cause a deadlock if this is the last reference
+		// Dispatch request in an external thread in case it needs to be destroyed
+		node->background ([client, pull] ()
+		{
+			client->request (pull);
+		});
+	}
 }
 
 bool rai::bootstrap_attempt::request_push (std::unique_lock <std::mutex> & lock_a)
@@ -854,31 +859,31 @@ void rai::bootstrap_attempt::run ()
 	auto frontier_failure (true);
 	while (!stopped && frontier_failure)
 	{
-        frontier_failure = request_frontier (lock);
+		frontier_failure = request_frontier (lock);
 	}
 	while (!stopped && (!pulls.empty () || pulling > 0))
 	{
-        if (!pulls.empty ())
-        {
-            request_pull (lock);
-        }
-        else
-        {
-            condition.wait (lock);
-        }
+		if (!pulls.empty ())
+		{
+			request_pull (lock);
+		}
+		else
+		{
+			condition.wait (lock);
+		}
+	}
+	if (!stopped)
+	{
+		BOOST_LOG (node->log) << "Completed pulls";
 	}
-    if (!stopped)
-    {
-        BOOST_LOG (node->log) << "Completed pulls";
-    }
 	auto push_failure (true);
 	while (!stopped && push_failure)
 	{
-        push_failure = request_push (lock);
+		push_failure = request_push (lock);
 	}
-    stopped = true;
+	stopped = true;
 	condition.notify_all ();
-    idle.clear ();
+	idle.clear ();
 }
 
 std::shared_ptr <rai::bootstrap_client> rai::bootstrap_attempt::connection (std::unique_lock <std::mutex> & lock_a)
```
