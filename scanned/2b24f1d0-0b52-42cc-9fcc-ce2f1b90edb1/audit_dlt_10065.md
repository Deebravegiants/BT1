# [?] Fix race condition in `vote_router::disconnect (...)` when election is concurrently erased (#5010)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-01-25
Source: https://github.com/nanocurrency/nano-node/commit/ea3fb2ac2f2b4d277c6f71083c4100f7c94dd35c
Type: security-commit

## Details
Fix race condition in `vote_router::disconnect (...)` when election is concurrently erased (#5010)

## Patch
### nano/node/vote_router.cpp
```diff
@@ -23,29 +23,51 @@ nano::vote_router::~vote_router ()
 	debug_assert (!thread.joinable ());
 }
 
+void nano::vote_router::start ()
+{
+	thread = std::thread{ [this] () {
+		nano::thread_role::set (nano::thread_role::name::vote_router);
+		run ();
+	} };
+}
+
+void nano::vote_router::stop ()
+{
+	{
+		std::unique_lock lock{ mutex };
+		stopped = true;
+	}
+	condition.notify_all ();
+	if (thread.joinable ())
+	{
+		thread.join ();
+	}
+}
+
 void nano::vote_router::connect (nano::block_hash const & hash, std::weak_ptr<nano::election> election)
 {
 	std::unique_lock lock{ mutex };
 	elections.insert_or_assign (hash, election);
 }
 
-void nano::vote_router::disconnect (nano::election const & election)
+std::size_t nano::vote_router::disconnect (nano::election const & election)
 {
 	std::unique_lock lock{ mutex };
+	std::size_t erased = 0;
 	for (auto const & [hash, _] : election.blocks ())
 	{
-		elections.erase (hash);
+		erased += elections.erase (hash);
 	}
+	return erased;
 }
 
-void nano::vote_router::disconnect (nano::block_hash const & hash)
+bool nano::vote_router::disconnect (nano::block_hash const & hash)
 {
 	std::unique_lock lock{ mutex };
-	[[maybe_unused]] auto erased = elections.erase (hash);
-	debug_assert (erased == 1);
+	auto erased = elections.erase (hash);
+	return erased > 0;
 }
 
-// Validate a vote and apply it to the current election if one exists
 std::unordered_map<nano::block_hash, nano::vote_code> nano::vote_router::vote (std::shared_ptr<nano::vote> const & vote, nano::vote_source source, nano::block_hash filter)
 {
 	debug_assert (!vote->validate ()); // false => valid vote
@@ -146,31 +168,19 @@ std::shared_ptr<nano::election> nano::vote_router::election (nano::block_hash co
 	return nullptr;
 }
 
-// This is meant to be a fast check and may return false positives if weak pointers have expired, but we don't care about that here
 bool nano::vote_router::contains (nano::block_hash const & hash) const
 {
 	std::shared_lock lock{ mutex };
 	return elections.contains (hash);
 }
 
-void nano::vote_router::start ()
+nano::container_info nano::vote_router::container_info () const
 {
-	thread = std::thread{ [this] () {
-		nano::thread_role::set (nano::thread_role::name::vote_router);
-		run ();
-	} };
-}
+	std::shared_lock lock{ mutex };
 
-void nano::vote_router::stop ()
-{
-	std::unique_lock lock{ mutex };
-	stopped = true;
-	lock.unlock ();
-	condition.notify_all ();
-	if (thread.joinable ())
-	{
-		thread.join ();
-	}
+	nano::container_info info;
+	info.put ("elections", elections);
+	return info;
 }
 
 void nano::vote_router::run ()
@@ -183,15 +193,6 @@ void nano::vote_router::run ()
 	}
 }
 
-nano::container_info nano::vote_router::container_info () const
-{
-	std::shared_lock lock{ mutex };
-
-	nano::container_info info;
-	info.put ("elections", elections);
-	return info;
-}
-
 /*
  *
  */
@@ -214,4 +215,4 @@ nano::stat::detail nano::to_stat_detail (nano::vote_source source)
 std::string_view nano::to_string (nano::vote_source source)
 {
 	return nano::enum_to_string (source);
-}
\ No newline at end of file
+}
```

### nano/node/vote_router.hpp
```diff
@@ -4,6 +4,7 @@
 #include <nano/lib/numbers_templ.hpp>
 #include <nano/node/fwd.hpp>
 
+#include <condition_variable>
 #include <memory>
 #include <shared_mutex>
 #include <thread>
@@ -34,55 +35,68 @@ enum class vote_source
 nano::stat::detail to_stat_detail (vote_source);
 std::string_view to_string (vote_source);
 
-// This class routes votes to their associated election
-// This class holds a weak_ptr as this container does not own the elections
-// Routing entries are removed periodically if the weak_ptr has expired
+/**
+ * Routes votes to their associated elections.
+ * Holds weak_ptr to elections as this container does not own them.
+ * Routing entries are removed periodically if the weak_ptr has expired.
+ */
 class vote_router final
 {
 public:
-	vote_router (nano::vote_cache & cache, nano::recently_confirmed_cache & recently_confirmed);
+	vote_router (nano::vote_cache &, nano::recently_confirmed_cache &);
 	~vote_router ();
 
 	void start ();
 	void stop ();
 
-	// Add a route for 'hash' to 'election'
-	// Existing routes will be replaced
-	// Election must hold the block for the hash being passed in
+	/**
+	 * Add a route for 'hash' to 'election'.
+	 * Existing routes will be replaced.
+	 * Election must hold the block for the hash being passed in.
+	 */
 	void connect (nano::block_hash const & hash, std::weak_ptr<nano::election> election);
-	// Remove all routes to this election
-	void disconnect (nano::election const & election);
-	void disconnect (nano::block_hash const & hash);
-	// Route vote to associated elections
-	// Distinguishes replay votes, cannot be determined if the block is not in any election
-
-	// If 'filter' parameter is non-zero, only elections for the specified hash are notified.
-	// This eliminates duplicate processing when triggering votes from the vote_cache as the result of a specific election being created.
+	/**
+	 * Remove all routes to this election.
+	 * @return number of routes removed
+	 */
+	std::size_t disconnect (nano::election const & election);
+	/**
+	 * Remove route for hash.
+	 * @return true if route existed and was removed
+	 */
+	bool disconnect (nano::block_hash const & hash);
+
+	/**
+	 * Route vote to associated elections.
+	 * Distinguishes replay votes, cannot be determined if the block is not in any election.
+	 * If 'filter' parameter is non-zero, only elections for the specified hash are notified.
+	 * This eliminates duplicate processing when triggering votes from the vote_cache as the result of a specific election being created.
+	 */
 	std::unordered_map<nano::block_hash, nano::vote_code> vote (std::shared_ptr<nano::vote> const &, nano::vote_source = nano::vote_source::live, nano::block_hash filter = { 0 });
+
 	bool active (nano::block_hash const & hash) const;
 	std::shared_ptr<nano::election> election (nano::block_hash const & hash) const;
 	bool contains (nano::block_hash const & hash) const;
 
+	nano::container_info container_info () const;
+
+public: // Events
 	using vote_processed_event_t = nano::observer_set<std::shared_ptr<nano::vote> const &, nano::vote_source, std::unordered_map<nano::block_hash, nano::vote_code> const &>;
 	vote_processed_event_t vote_processed;
 
-	nano::container_info container_info () const;
-
 private: // Dependencies
 	nano::vote_cache & vote_cache;
 	nano::recently_confirmed_cache & recently_confirmed;
 
 private:
 	void run ();
 
-private:
-	// Mapping of block hashes to elections.
-	// Election already contains the associated block
+	// Mapping of block hashes to elections
 	std::unordered_map<nano::block_hash, std::weak_ptr<nano::election>> elections;
 
 	bool stopped{ false };
-	std::condition_variable_any condition;
 	mutable std::shared_mutex mutex;
+	std::condition_variable_any condition;
 	std::thread thread;
 };
 }
```
