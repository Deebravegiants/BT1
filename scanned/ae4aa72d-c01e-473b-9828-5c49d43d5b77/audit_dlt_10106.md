# [?] Fixing deadlock of client exits during initial run.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-03-14
Source: https://github.com/nanocurrency/nano-node/commit/fe889f528287f6ab87e9aa665efa6d574fb50a81
Type: security-commit

## Details
Fixing deadlock of client exits during initial run.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -759,15 +759,21 @@ rai::bootstrap_attempt::~bootstrap_attempt ()
 
 void rai::bootstrap_attempt::attempt (rai::endpoint const & endpoint_a)
 {
-	std::lock_guard <std::mutex> lock (mutex);
-	if (!connected)
+	auto this_l (shared_from_this ());
+	std::shared_ptr <rai::bootstrap_client> client;
+	{
+		std::lock_guard <std::mutex> lock (mutex);
+		if (!connected)
+		{
+			BOOST_LOG (node->log) << boost::str (boost::format ("Initiating bootstrap to: %1%") % endpoint_a);
+			auto node_l (node->shared ());
+			client = std::make_shared <rai::bootstrap_client> (node_l, this_l);
+			connecting [client.get ()] = client;
+		}
+	}
+	if (client)
 	{
-		BOOST_LOG (node->log) << boost::str (boost::format ("Initiating bootstrap to: %1%") % endpoint_a);
-		auto node_l (node->shared ());
-		auto this_l (shared_from_this ());
-		auto processor (std::make_shared <rai::bootstrap_client> (node_l, this_l));
-		connecting [processor.get ()] = processor;
-		processor->run (rai::tcp_endpoint (endpoint_a.address (), endpoint_a.port ()));
+		client->run (rai::tcp_endpoint (endpoint_a.address (), endpoint_a.port ()));
 		node->alarm.add (std::chrono::system_clock::now () + std::chrono::milliseconds (250), [this_l] ()
 		{
 			this_l->attempt ();
```
