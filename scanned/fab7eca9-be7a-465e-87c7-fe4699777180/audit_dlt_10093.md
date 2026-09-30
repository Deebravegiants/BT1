# [?] Fixed a rare yet possible race condition which would cause a crash.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-01-04
Source: https://github.com/nanocurrency/nano-node/commit/2bd3d235688b41832553a0e44301539a01bbce7e
Type: security-commit

## Details
Fixed a rare yet possible race condition which would cause a crash.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -1355,55 +1355,55 @@ namespace
 class request_response_visitor : public rai::message_visitor
 {
 public:
-    request_response_visitor (std::shared_ptr <rai::bootstrap_server> connection_a) :
-    connection (connection_a)
-    {
-    }
-    void keepalive (rai::keepalive const &) override
-    {
-        assert (false);
-    }
-    void publish (rai::publish const &) override
-    {
-        assert (false);
-    }
-    void confirm_req (rai::confirm_req const &) override
-    {
-        assert (false);
-    }
-    void confirm_ack (rai::confirm_ack const &) override
-    {
-        assert (false);
-    }
-    void bulk_pull (rai::bulk_pull const &) override
-    {
-        auto response (std::make_shared <rai::bulk_pull_server> (connection, std::unique_ptr <rai::bulk_pull> (static_cast <rai::bulk_pull *> (connection->requests.front ().release ()))));
-        response->send_next ();
-    }
-    void bulk_push (rai::bulk_push const &) override
-    {
-        auto response (std::make_shared <rai::bulk_push_server> (connection));
-        response->receive ();
-    }
-    void frontier_req (rai::frontier_req const &) override
-    {
-        auto response (std::make_shared <rai::frontier_req_server> (connection, std::unique_ptr <rai::frontier_req> (static_cast <rai::frontier_req *> (connection->requests.front ().release ()))));
-        response->send_next ();
-    }
-    std::shared_ptr <rai::bootstrap_server> connection;
+	request_response_visitor (std::shared_ptr <rai::bootstrap_server> connection_a) :
+	connection (connection_a)
+	{
+	}
+	void keepalive (rai::keepalive const &) override
+	{
+		assert (false);
+	}
+	void publish (rai::publish const &) override
+	{
+		assert (false);
+	}
+	void confirm_req (rai::confirm_req const &) override
+	{
+		assert (false);
+	}
+	void confirm_ack (rai::confirm_ack const &) override
+	{
+		assert (false);
+	}
+	void bulk_pull (rai::bulk_pull const &) override
+	{
+		auto response (std::make_shared <rai::bulk_pull_server> (connection, std::unique_ptr <rai::bulk_pull> (static_cast <rai::bulk_pull *> (connection->requests.front ().release ()))));
+		response->send_next ();
+	}
+	void bulk_push (rai::bulk_push const &) override
+	{
+		auto response (std::make_shared <rai::bulk_push_server> (connection));
+		response->receive ();
+	}
+	void frontier_req (rai::frontier_req const &) override
+	{
+		auto response (std::make_shared <rai::frontier_req_server> (connection, std::unique_ptr <rai::frontier_req> (static_cast <rai::frontier_req *> (connection->requests.front ().release ()))));
+		response->send_next ();
+	}
+	std::shared_ptr <rai::bootstrap_server> connection;
 };
 }
 
 void rai::bootstrap_server::run_next ()
 {
 	assert (!requests.empty ());
-    request_response_visitor visitor (shared_from_this ());
-    requests.front ()->visit (visitor);
+	request_response_visitor visitor (shared_from_this ());
+	requests.front ()->visit (visitor);
 }
 
 void rai::bulk_pull_server::set_current_end ()
 {
-    assert (request != nullptr);
+	assert (request != nullptr);
 	rai::transaction transaction (connection->node->store.environment, nullptr, false);
 	if (!connection->node->store.block_exists (transaction, request->end))
 	{
@@ -1446,57 +1446,63 @@ void rai::bulk_pull_server::set_current_end ()
 
 void rai::bulk_pull_server::send_next ()
 {
-    std::unique_ptr <rai::block> block (get_next ());
-    if (block != nullptr)
-    {
-        {
-            send_buffer.clear ();
-            rai::vectorstream stream (send_buffer);
-            rai::serialize_block (stream, *block);
-        }
-        auto this_l (shared_from_this ());
-        if (connection->node->config.logging.bulk_pull_logging ())
-        {
-            BOOST_LOG (connection->node->log) << boost::str (boost::format ("Sending block: %1%") % block->hash ().to_string ());
-        }
-        async_write (*connection->socket, boost::asio::buffer (send_buffer.data (), send_buffer.size ()), [this_l] (boost::system::error_code const & ec, size_t size_a)
-        {
-            this_l->sent_action (ec, size_a);
-        });
-    }
-    else
-    {
-        send_finished ();
-    }
+	std::unique_ptr <rai::block> block (get_next ());
+	if (block != nullptr)
+	{
+		{
+			send_buffer.clear ();
+			rai::vectorstream stream (send_buffer);
+			rai::serialize_block (stream, *block);
+		}
+		auto this_l (shared_from_this ());
+		if (connection->node->config.logging.bulk_pull_logging ())
+		{
+			BOOST_LOG (connection->node->log) << boost::str (boost::format ("Sending block: %1%") % block->hash ().to_string ());
+		}
+		async_write (*connection->socket, boost::asio::buffer (send_buffer.data (), send_buffer.size ()), [this_l] (boost::system::error_code const & ec, size_t size_a)
+		{
+			this_l->sent_action (ec, size_a);
+		});
+	}
+	else
+	{
+		send_finished ();
+	}
 }
 
 std::unique_ptr <rai::block> rai::bulk_pull_server::get_next ()
 {
-    std::unique_ptr <rai::block> result;
-    if (current != request->end)
-    {
+	std::unique_ptr <rai::block> result;
+	if (current != request->end)
+	{
 		rai::transaction transaction (connection->node->store.environment, nullptr, false);
-        result = connection->node->store.block_get (transaction, current);
-        assert (result != nullptr);
-        auto previous (result->previous ());
-        if (!previous.is_zero ())
-        {
-            current = previous;
-        }
-        else
-        {
-            request->end = current;
-        }
-    }
-    return result;
+		result = connection->node->store.block_get (transaction, current);
+		if (result != nullptr)
+		{
+			auto previous (result->previous ());
+			if (!previous.is_zero ())
+			{
+				current = previous;
+			}
+			else
+			{
+				current = request->end;
+			}
+		}
+		else
+		{
+			current = request->end;
+		}
+	}
+	return result;
 }
 
 void rai::bulk_pull_server::sent_action (boost::system::error_code const & ec, size_t size_a)
 {
-    if (!ec)
-    {
-        send_next ();
-    }
+	if (!ec)
+	{
+		send_next ();
+	}
 	else
 	{
 		BOOST_LOG (connection->node->log) << boost::str (boost::format ("Unable to bulk send block: %1%") % ec.message ());
@@ -1505,26 +1511,26 @@ void rai::bulk_pull_server::sent_action (boost::system::error_code const & ec, s
 
 void rai::bulk_pull_server::send_finished ()
 {
-    send_buffer.clear ();
-    send_buffer.push_back (static_cast <uint8_t> (rai::block_type::not_a_block));
-    auto this_l (shared_from_this ());
-    if (connection->node->config.logging.bulk_pull_logging ())
-    {
-        BOOST_LOG (connection->node->log) << "Bulk sending finished";
-    }
-    async_write (*connection->socket, boost::asio::buffer (send_buffer.data (), 1), [this_l] (boost::system::error_code const & ec, size_t size_a)
-    {
-        this_l->no_block_sent (ec, size_a);
-    });
+	send_buffer.clear ();
+	send_buffer.push_back (static_cast <uint8_t> (rai::block_type::not_a_block));
+	auto this_l (shared_from_this ());
+	if (connection->node->config.logging.bulk_pull_logging ())
+	{
+		BOOST_LOG (connection->node->log) << "Bulk sending finished";
+	}
+	async_write (*connection->socket, boost::asio::buffer (send_buffer.data (), 1), [this_l] (boost::system::error_code const & ec, size_t size_a)
+	{
+		this_l->no_block_sent (ec, size_a);
+	});
 }
 
 void rai::bulk_pull_server::no_block_sent (boost::system::error_code const & ec, size_t size_a)
 {
-    if (!ec)
-    {
-        assert (size_a == 1);
+	if (!ec)
+	{
+		assert (size_a == 1);
 		connection->finish_request ();
-    }
+	}
 	else
 	{
 		BOOST_LOG (connection->node->log) << "Unable to send not-a-block";
@@ -1535,7 +1541,7 @@ rai::bulk_pull_server::bulk_pull_server (std::shared_ptr <rai::bootstrap_server>
 connection (connection_a),
 request (std::move (request_a))
 {
-    set_current_end ();
+	set_current_end ();
 }
 
 rai::bulk_push_server::bulk_push_server (std::shared_ptr <rai::bootstrap_server> const & connection_a) :
```
