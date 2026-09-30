# [?] fix race condition between bootstrap pull and push (#3721)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2022-02-08
Source: https://github.com/nanocurrency/nano-node/commit/ddf07f156b31d18a599de942ec79e0e30b72d9c5
Type: security-commit

## Details
fix race condition between bootstrap pull and push (#3721)

The unit test bootstrap_processor.push_one fails intermittently and it
exposes a race condition in the bootstrap code of the node. #3533

The race condition is that after finishing with bootstrap frontiers pull,
the code is supposed to put the socket back into the idle bootstrap
connections queue. However it does that in a racy way. The problem is in
the function nano::frontier_req_client::received_frontier.

Near the bottom of that function, we should call:
connection->connections.pool_connection (connection);
before calling
promise.set_value (false);

Once the promise is given a value then
nano::bootstrap_attempt_legacy::run()
continues to call push_request in parallel with pool_connection and it is
a race condition.

Although this is a bug, this is likely not a major nor catastrophic bug
because the bootstrap push functionality is only an efficiency.

resolves #3533
resolves #3720

## Patch
### nano/core_test/bootstrap.cpp
```diff
@@ -459,10 +459,7 @@ TEST (bootstrap_processor, DISABLED_push_diamond_pruning)
 	node1->stop ();
 }
 
-// Test disabled because it's failing intermittently.
-// PR in which it got disabled: https://github.com/nanocurrency/nano-node/pull/3532
-// Issue for investigating it: https://github.com/nanocurrency/nano-node/issues/3533
-TEST (bootstrap_processor, DISABLED_push_one)
+TEST (bootstrap_processor, push_one)
 {
 	nano::system system;
 	nano::node_config config (nano::get_available_port (), system.logging);
```

### nano/node/bootstrap/bootstrap_frontier.cpp
```diff
@@ -192,14 +192,14 @@ void nano::frontier_req_client::received_frontier (boost::system::error_code con
 				// Set last processed account as new start target
 				attempt->set_start_account (last_account);
 			}
+			connection->connections.pool_connection (connection);
 			try
 			{
 				promise.set_value (false);
 			}
 			catch (std::future_error &)
 			{
 			}
-			connection->connections.pool_connection (connection);
 		}
 	}
 	else
```
