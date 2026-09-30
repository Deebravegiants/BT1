# [?] Fix for channels::transaction_ack not always being called on expired or invalid signature transactions.

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2022-08-23
Source: https://github.com/AntelopeIO/leap/commit/81a249c09df1af851df9e59cdf26bd0cc37d34c8
Type: security-commit

## Details
Fix for channels::transaction_ack not always being called on expired or invalid signature transactions.

## Patch
### plugins/producer_plugin/producer_plugin.cpp
```diff
@@ -499,8 +499,23 @@ class producer_plugin_impl : public std::enable_shared_from_this<producer_plugin
                                                                  read_only ? transaction_metadata::trx_type::read_only : transaction_metadata::trx_type::input,
                                                                  chain.configured_subjective_signature_length_limit() );
 
+         if( !read_only ) {
+            next = [this, trx, next{std::move(next)}]( const std::variant<fc::exception_ptr, transaction_trace_ptr>& response ) {
+               next( response );
+
+               fc::exception_ptr except_ptr; // rejected
+               if( std::holds_alternative<fc::exception_ptr>( response ) ) {
+                  except_ptr = std::get<fc::exception_ptr>( response );
+               } else if( std::get<transaction_trace_ptr>( response )->except ) {
+                  except_ptr = std::get<transaction_trace_ptr>( response )->except->dynamic_copy_exception();
+               }
+
+               _transaction_ack_channel.publish( priority::low, std::pair<fc::exception_ptr, packed_transaction_ptr>( except_ptr, trx ) );
+            };
+         }
+
          boost::asio::post(_thread_pool->get_executor(), [self = this, future{std::move(future)}, persist_until_expired, return_failure_traces,
-                                                          next{std::move(next)}, trx]() mutable {
+                                                          next{std::move(next)}, trx=trx]() mutable {
             if( future.valid() ) {
                future.wait();
                app().post( priority::low, [self, future{std::move(future)}, persist_until_expired, next{std::move( next )}, trx{std::move(trx)}, return_failure_traces]() mutable {
@@ -537,21 +552,6 @@ class producer_plugin_impl : public std::enable_shared_from_this<producer_plugin
          auto start = fc::time_point::now();
          chain::controller& chain = chain_plug->chain();
 
-         auto send_response = [this, &trx, &next](const std::variant<fc::exception_ptr, transaction_trace_ptr>& response) {
-            next(response);
-
-            if (!trx->read_only) {
-               fc::exception_ptr except_ptr; // rejected
-               if (std::holds_alternative<fc::exception_ptr>(response)) {
-                  except_ptr = std::get<fc::exception_ptr>(response);
-               } else if (std::get<transaction_trace_ptr>(response)->except) {
-                  except_ptr = std::get<transaction_trace_ptr>(response)->except->dynamic_copy_exception();
-               }
-
-               _transaction_ack_channel.publish(priority::low, std::pair<fc::exception_ptr, packed_transaction_ptr>(except_ptr, trx->packed_trx()));
-            }
-         };
-
          try {
             const auto& id = trx->id();
 
@@ -563,15 +563,15 @@ class producer_plugin_impl : public std::enable_shared_from_this<producer_plugin
                            FC_LOG_MESSAGE( error, "expired transaction ${id}, expiration ${e}, block time ${bt}",
                                            ("id", id)("e", expire)("bt", bt))));
                log_trx_results( trx, nullptr, except_ptr, 0, start );
-               send_response( std::move(except_ptr) );
+               next( std::move(except_ptr) );
                return true;
             }
 
             if( chain.is_known_unexpired_transaction( id )) {
                auto except_ptr = std::static_pointer_cast<fc::exception>( std::make_shared<tx_duplicate>(
                      FC_LOG_MESSAGE( error, "duplicate transaction ${id}", ("id", id))));
                log_trx_results( trx, nullptr, except_ptr, 0, start );
-               send_response( std::move(except_ptr) );
+               next( std::move(except_ptr) );
                return true;
             }
 
@@ -581,7 +581,7 @@ class producer_plugin_impl : public std::enable_shared_from_this<producer_plugin
             }
 
             const auto block_deadline = calculate_block_deadline( chain.pending_block_time() );
-            push_result pr = push_transaction( block_deadline, trx, persist_until_expired, return_failure_trace, send_response );
+            push_result pr = push_transaction( block_deadline, trx, persist_until_expired, return_failure_trace, next );
 
             exhausted = pr.block_exhausted;
             if( pr.trx_exhausted ) {
@@ -596,7 +596,7 @@ class producer_plugin_impl : public std::enable_shared_from_this<producer_plugin
             chain_plugin::handle_db_exhaustion();
          } catch ( std::bad_alloc& ) {
             chain_plugin::handle_bad_alloc();
-         } CATCH_AND_CALL(send_response);
+         } CATCH_AND_CALL(next);
 
          _idle_trx_time = fc::time_point::now();
          return !exhausted;
```

### plugins/producer_plugin/test/test_trx_full.cpp
```diff
@@ -136,6 +136,13 @@ BOOST_AUTO_TEST_CASE(producer) {
       auto bs = chain_plug->chain().block_start.connect( [&]( uint32_t bn ) {
       } );
 
+      std::atomic<size_t> num_acked = 0;
+      plugin_interface::compat::channels::transaction_ack::channel_type::handle incoming_transaction_ack_subscription =
+            appbase::app().get_channel<plugin_interface::compat::channels::transaction_ack>().subscribe(
+                  [&num_acked]( const std::pair<fc::exception_ptr, packed_transaction_ptr>& t){
+                     ++num_acked;
+                  } );
+
       std::deque<packed_transaction_ptr> trxs;
       std::atomic<size_t> next_calls = 0;
       std::atomic<size_t> num_posts = 0;
@@ -189,6 +196,7 @@ BOOST_AUTO_TEST_CASE(producer) {
       BOOST_CHECK( all_blocks.size() > 3 ); // should have a few blocks otherwise test is running too fast
       BOOST_CHECK_EQUAL( num_pushes, num_posts );
       BOOST_CHECK_EQUAL( num_pushes, next_calls );
+      BOOST_CHECK_EQUAL( num_pushes, num_acked );
       BOOST_CHECK( trx_match.load() );
 
       appbase::app().quit();
```
