# [?] node_server: fix race condition

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-09-20
Source: https://github.com/monero-project/monero/commit/9154883f3ef76c54552adcb0fddffe135d206cf6
Type: security-commit

## Details
node_server: fix race condition

## Patch
### src/cryptonote_protocol/levin_notify.cpp
```diff
@@ -287,6 +287,12 @@ namespace levin
       boost::asio::steady_timer next_epoch;
       boost::asio::steady_timer flush_txs;
       boost::asio::io_service::strand strand;
+      struct context_t {
+        std::vector<cryptonote::blobdata> fluff_txs;
+        std::chrono::steady_clock::time_point flush_time;
+        bool m_is_income;
+      };
+      boost::unordered_map<boost::uuids::uuid, context_t> contexts;
       net::dandelionpp::connection_map map;//!< Tracks outgoing uuid's for noise channels or Dandelion++ stems
       std::deque<noise_channel> channels;  //!< Never touch after init; only update elements on `noise_channel.strand`
       std::atomic<std::size_t> connection_count; //!< Only update in strand, can be read at any time
@@ -363,23 +369,24 @@ namespace levin
         const auto now = std::chrono::steady_clock::now();
         auto next_flush = std::chrono::steady_clock::time_point::max();
         std::vector<std::pair<std::vector<blobdata>, boost::uuids::uuid>> connections{};
-        zone_->p2p->foreach_connection([timer_error, now, &next_flush, &connections] (detail::p2p_context& context)
+        for (auto &e: zone_->contexts)
         {
+          auto &id = e.first;
+          auto &context = e.second;
           if (!context.fluff_txs.empty())
           {
             if (context.flush_time <= now || timer_error) // flush on canceled timer
             {
               context.flush_time = std::chrono::steady_clock::time_point::max();
-              connections.emplace_back(std::move(context.fluff_txs), context.m_connection_id);
+              connections.emplace_back(std::move(context.fluff_txs), id);
               context.fluff_txs.clear();
             }
             else // not flushing yet
               next_flush = std::min(next_flush, context.flush_time);
           }
           else // nothing to flush
             context.flush_time = std::chrono::steady_clock::time_point::max();
-          return true;
-        });
+        }
 
         /* Always send with `fluff` flag, even over i2p/tor. The hidden service
 	   will disable the forwarding delay and immediately fluff. The i2p/tor
@@ -427,22 +434,21 @@ namespace levin
 
 
         MDEBUG("Queueing " << txs.size() << " transaction(s) for Dandelion++ fluffing");
-
-        zone->p2p->foreach_connection([txs, now, &zone, &source, &in_duration, &out_duration, &next_flush] (detail::p2p_context& context)
+        for (auto &e: zone->contexts)
         {
+          auto &id = e.first;
+          auto &context = e.second;
           // When i2p/tor, only fluff to outbound connections
-          if (context.handshake_complete() && source != context.m_connection_id && (zone->nzone == epee::net_utils::zone::public_ || !context.m_is_income))
+          if (source != id && (zone->nzone == epee::net_utils::zone::public_ || !context.m_is_income))
           {
             if (context.fluff_txs.empty())
               context.flush_time = now + (context.m_is_income ? in_duration() : out_duration());
 
             next_flush = std::min(next_flush, context.flush_time);
             context.fluff_txs.reserve(context.fluff_txs.size() + txs.size());
-            for (const blobdata& tx : txs)
-              context.fluff_txs.push_back(tx); // must copy instead of move (multiple conns)
+            context.fluff_txs.insert(context.fluff_txs.end(), txs.begin(), txs.end());
           }
-          return true;
-        });
+        }
 
         if (next_flush == std::chrono::steady_clock::time_point::max())
           MWARNING("Unable to send transaction(s), no available connections");
@@ -749,6 +755,32 @@ namespace levin
     );
   }
 
+  void notify::on_handshake_complete(const boost::uuids::uuid &id, bool is_income)
+  {
+    if (!zone_)
+      return;
+
+    auto& zone = zone_;
+    zone_->strand.dispatch([zone, id, is_income]{
+      zone->contexts[id] = {
+        .fluff_txs = {},
+        .flush_time = std::chrono::steady_clock::time_point::max(),
+        .m_is_income = is_income,
+      };
+    });
+  }
+
+  void notify::on_connection_close(const boost::uuids::uuid &id)
+  {
+    if (!zone_)
+      return;
+
+    auto& zone = zone_;
+    zone_->strand.dispatch([zone, id]{
+      zone->contexts.erase(id);
+    });
+  }
+
   void notify::run_epoch()
   {
     if (!zone_)
```

### src/cryptonote_protocol/levin_notify.h
```diff
@@ -101,6 +101,9 @@ namespace levin
     //! Probe for new outbound connection - skips if not needed.
     void new_out_connection();
 
+    void on_handshake_complete(const boost::uuids::uuid &id, bool is_income);
+    void on_connection_close(const boost::uuids::uuid &id);
+
     //! Run the logic for the next epoch immediately. Only use in testing.
     void run_epoch();
 
```

### src/p2p/net_node.h
```diff
@@ -111,15 +111,11 @@ namespace nodetool
   struct p2p_connection_context_t: base_type //t_payload_net_handler::connection_context //public net_utils::connection_context_base
   {
     p2p_connection_context_t()
-      : fluff_txs(),
-        flush_time(std::chrono::steady_clock::time_point::max()),
-        peer_id(0),
+      : peer_id(0),
         support_flags(0),
         m_in_timedsync(false)
     {}
 
-    std::vector<cryptonote::blobdata> fluff_txs;
-    std::chrono::steady_clock::time_point flush_time;
     peerid_type peer_id;
     uint32_t support_flags;
     bool m_in_timedsync;
```

### src/p2p/net_node.inl
```diff
@@ -1412,6 +1412,7 @@ namespace nodetool
     ape.first_seen = first_seen_stamp ? first_seen_stamp : time(nullptr);
 
     zone.m_peerlist.append_with_peer_anchor(ape);
+    zone.m_notifier.on_handshake_complete(con->m_connection_id, con->m_is_income);
     zone.m_notifier.new_out_connection();
 
     LOG_DEBUG_CC(*con, "CONNECTION HANDSHAKED OK.");
@@ -2526,6 +2527,8 @@ namespace nodetool
       return 1;
     }
 
+    zone.m_notifier.on_handshake_complete(context.m_connection_id, context.m_is_income);
+
     if(has_too_many_connections(context.m_remote_address))
     {
       LOG_PRINT_CCONTEXT_L1("CONNECTION FROM " << context.m_remote_address.host_str() << " REFUSED, too many connections from the same address");
@@ -2652,6 +2655,9 @@ namespace nodetool
       zone.m_peerlist.remove_from_peer_anchor(na);
     }
 
+    if (!zone.m_net_server.is_stop_signal_sent()) {
+      zone.m_notifier.on_connection_close(context.m_connection_id);
+    }
     m_payload_handler.on_connection_close(context);
 
     MINFO("["<< epee::net_utils::print_connection_context(context) << "] CLOSE CONNECTION");
```

### tests/unit_tests/levin.cpp
```diff
@@ -265,11 +265,17 @@ namespace
         virtual void callback(cryptonote::levin::detail::p2p_context& context) override final
         {}
 
-        virtual void on_connection_new(cryptonote::levin::detail::p2p_context&) override final
-        {}
+        virtual void on_connection_new(cryptonote::levin::detail::p2p_context& context) override final
+        {
+            if (notifier)
+                notifier->on_handshake_complete(context.m_connection_id, context.m_is_income);
+        }
 
-        virtual void on_connection_close(cryptonote::levin::detail::p2p_context&) override final
-        {}
+        virtual void on_connection_close(cryptonote::levin::detail::p2p_context& context) override final
+        {
+            if (notifier)
+                notifier->on_connection_close(context.m_connection_id);
+        }
 
     public:
         test_receiver()
@@ -306,6 +312,8 @@ namespace
         {
             return get_raw_message(notified_);
         }
+
+        std::shared_ptr<cryptonote::levin::notify> notifier{};
     };
 
     class levin_notify : public ::testing::Test
@@ -343,13 +351,16 @@ namespace
             EXPECT_EQ(connection_ids_.size(), connections_->get_connections_count());
         }
 
-        cryptonote::levin::notify make_notifier(const std::size_t noise_size, bool is_public, bool pad_txs)
+        std::shared_ptr<cryptonote::levin::notify> make_notifier(const std::size_t noise_size, bool is_public, bool pad_txs)
         {
             epee::byte_slice noise = nullptr;
             if (noise_size)
                 noise = epee::levin::make_noise_notify(noise_size);
             epee::net_utils::zone zone = is_public ? epee::net_utils::zone::public_ : epee::net_utils::zone::i2p;
-            return cryptonote::levin::notify{io_service_, connections_, std::move(noise), zone, pad_txs, events_};
+            receiver_.notifier.reset(
+              new cryptonote::levin::notify{io_service_, connections_, std::move(noise), zone, pad_txs, events_}
+            );
+            return receiver_.notifier;
         }
 
         boost::uuids::random_generator random_generator_;
@@ -590,7 +601,8 @@ TEST_F(levin_notify, defaulted)
 
 TEST_F(levin_notify, fluff_without_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -636,7 +648,8 @@ TEST_F(levin_notify, fluff_without_padding)
 
 TEST_F(levin_notify, stem_without_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -708,7 +721,8 @@ TEST_F(levin_notify, stem_without_padding)
 
 TEST_F(levin_notify, stem_no_outs_without_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(true);
@@ -764,7 +778,8 @@ TEST_F(levin_notify, stem_no_outs_without_padding)
 
 TEST_F(levin_notify, local_without_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -836,7 +851,8 @@ TEST_F(levin_notify, local_without_padding)
 
 TEST_F(levin_notify, forward_without_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -908,7 +924,8 @@ TEST_F(levin_notify, forward_without_padding)
 
 TEST_F(levin_notify, block_without_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -937,7 +954,8 @@ TEST_F(levin_notify, block_without_padding)
 
 TEST_F(levin_notify, none_without_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -966,7 +984,8 @@ TEST_F(levin_notify, none_without_padding)
 
 TEST_F(levin_notify, fluff_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1012,7 +1031,8 @@ TEST_F(levin_notify, fluff_with_padding)
 
 TEST_F(levin_notify, stem_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1079,7 +1099,8 @@ TEST_F(levin_notify, stem_with_padding)
 
 TEST_F(levin_notify, stem_no_outs_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(true);
@@ -1135,7 +1156,8 @@ TEST_F(levin_notify, stem_no_outs_with_padding)
 
 TEST_F(levin_notify, local_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1202,7 +1224,8 @@ TEST_F(levin_notify, local_with_padding)
 
 TEST_F(levin_notify, forward_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1269,7 +1292,8 @@ TEST_F(levin_notify, forward_with_padding)
 
 TEST_F(levin_notify, block_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1298,7 +1322,8 @@ TEST_F(levin_notify, block_with_padding)
 
 TEST_F(levin_notify, none_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, true, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1327,7 +1352,8 @@ TEST_F(levin_notify, none_with_padding)
 
 TEST_F(levin_notify, private_fluff_without_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, false, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1378,7 +1404,8 @@ TEST_F(levin_notify, private_fluff_without_padding)
 TEST_F(levin_notify, private_stem_without_padding)
 {
     // private mode always uses fluff but marked as stem
-    cryptonote::levin::notify notifier = make_notifier(0, false, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1429,7 +1456,8 @@ TEST_F(levin_notify, private_stem_without_padding)
 TEST_F(levin_notify, private_local_without_padding)
 {
     // private mode always uses fluff but marked as stem
-    cryptonote::levin::notify notifier = make_notifier(0, false, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1480,7 +1508,8 @@ TEST_F(levin_notify, private_local_without_padding)
 TEST_F(levin_notify, private_forward_without_padding)
 {
     // private mode always uses fluff but marked as stem
-    cryptonote::levin::notify notifier = make_notifier(0, false, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1531,7 +1560,8 @@ TEST_F(levin_notify, private_forward_without_padding)
 TEST_F(levin_notify, private_block_without_padding)
 {
     // private mode always uses fluff but marked as stem
-    cryptonote::levin::notify notifier = make_notifier(0, false, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1561,7 +1591,8 @@ TEST_F(levin_notify, private_block_without_padding)
 TEST_F(levin_notify, private_none_without_padding)
 {
     // private mode always uses fluff but marked as stem
-    cryptonote::levin::notify notifier = make_notifier(0, false, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1590,7 +1621,8 @@ TEST_F(levin_notify, private_none_without_padding)
 
 TEST_F(levin_notify, private_fluff_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, false, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1640,7 +1672,8 @@ TEST_F(levin_notify, private_fluff_with_padding)
 
 TEST_F(levin_notify, private_stem_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, false, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1690,7 +1723,8 @@ TEST_F(levin_notify, private_stem_with_padding)
 
 TEST_F(levin_notify, private_local_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, false, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1740,7 +1774,8 @@ TEST_F(levin_notify, private_local_with_padding)
 
 TEST_F(levin_notify, private_forward_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, false, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1790,7 +1825,8 @@ TEST_F(levin_notify, private_forward_with_padding)
 
 TEST_F(levin_notify, private_block_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, false, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1819,7 +1855,8 @@ TEST_F(levin_notify, private_block_with_padding)
 
 TEST_F(levin_notify, private_none_with_padding)
 {
-    cryptonote::levin::notify notifier = make_notifier(0, false, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, false, true);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < 10; ++count)
         add_connection(count % 2 == 0);
@@ -1850,7 +1887,8 @@ TEST_F(levin_notify, stem_mappings)
 {
     static constexpr const unsigned test_connections_count = (CRYPTONOTE_DANDELIONPP_STEMS + 1) * 2;
 
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < test_connections_count; ++count)
         add_connection(count % 2 == 0);
@@ -1973,7 +2011,8 @@ TEST_F(levin_notify, fluff_multiple)
 {
     static constexpr const unsigned test_connections_count = (CRYPTONOTE_DANDELIONPP_STEMS + 1) * 2;
 
-    cryptonote::levin::notify notifier = make_notifier(0, true, false);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(0, true, false);
+    auto &notifier = *notifier_ptr;
 
     for (unsigned count = 0; count < test_connections_count; ++count)
         add_connection(count % 2 == 0);
@@ -2091,7 +2130,8 @@ TEST_F(levin_notify, noise)
     txs[0].resize(1900, 'h');
 
     const boost::uuids::uuid incoming_id = random_generator_();
-    cryptonote::levin::notify notifier = make_notifier(2048, false, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(2048, false, true);
+    auto &notifier = *notifier_ptr;
 
     {
         const auto status = notifier.get_status();
@@ -2182,7 +2222,8 @@ TEST_F(levin_notify, noise_stem)
     txs[0].resize(1900, 'h');
 
     const boost::uuids::uuid incoming_id = random_generator_();
-    cryptonote::levin::notify notifier = make_notifier(2048, false, true);
+    std::shared_ptr<cryptonote::levin::notify> notifier_ptr = make_notifier(2048, false, true);
+    auto &notifier = *notifier_ptr;
 
     {
         const auto status = notifier.get_status();
```
