# [?] Adding non-deterministic sentinel values to avoid attacks due to well-known values.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-04-02
Source: https://github.com/nanocurrency/nano-node/commit/e5d7eb072b01291930ad6e548c30c6f64dda279a
Type: security-commit

## Details
Adding non-deterministic sentinel values to avoid attacks due to well-known values.

Using no_an_account sentinal in votes container instead of always using 0.

## Patch
### rai/secure.cpp
```diff
@@ -61,6 +61,9 @@ genesis_account (rai::rai_network == rai::rai_networks::rai_test_network ? rai_t
 genesis_block (rai::rai_network == rai::rai_networks::rai_test_network ? rai_test_genesis : rai::rai_network == rai::rai_networks::rai_beta_network ? rai_beta_genesis : rai_live_genesis),
 genesis_amount (std::numeric_limits <rai::uint128_t>::max ())
 {
+	// Randomly generating these mean no two nodes will ever have the same sentinal values which protects against some insecure algorithms
+	rai::random_pool.GenerateBlock (not_a_block.bytes.data (), not_a_block.bytes.size ());
+	rai::random_pool.GenerateBlock (not_an_account.bytes.data (), not_an_account.bytes.size ());
 }
 rai::keypair zero_key;
 rai::keypair test_genesis_key;
@@ -74,6 +77,8 @@ rai::account genesis_account;
 std::string genesis_block;
 rai::uint128_t genesis_amount;
 CryptoPP::AutoSeededRandomPool random_pool;
+rai::block_hash not_a_block;
+rai::account not_an_account;
 };
 ledger_constants globals;
 }
@@ -96,6 +101,8 @@ rai::account const & rai::genesis_account (globals.genesis_account);
 std::string const & rai::genesis_block (globals.genesis_block);
 rai::uint128_t const & rai::genesis_amount (globals.genesis_amount);
 CryptoPP::AutoSeededRandomPool & rai::random_pool (globals.random_pool);
+rai::block_hash const & rai::not_a_block (globals.not_a_block);
+rai::block_hash const & rai::not_an_account (globals.not_an_account);
 
 boost::filesystem::path rai::working_path ()
 {
@@ -163,7 +170,7 @@ std::map <rai::uint128_t, std::unique_ptr <rai::block>, std::greater <rai::uint1
 rai::votes::votes (rai::block const & block_a) :
 id (block_a.root ())
 {
-	rep_votes.insert (std::make_pair (0, block_a.clone ()));
+	rep_votes.insert (std::make_pair (rai::not_an_account, block_a.clone ()));
 }
 
 rai::tally_result rai::votes::vote (rai::vote const & vote_a)
```

### rai/secure.hpp
```diff
@@ -526,6 +526,10 @@ extern std::string const & rai_live_genesis;
 extern std::string const & genesis_block;
 extern rai::account const & genesis_account;
 extern rai::uint128_t const & genesis_amount;
+// A block hash that compares inequal to any real block hash
+extern rai::block_hash const & not_a_block;
+// An account number that compares inequal to any real account number
+extern rai::block_hash const & not_an_account;
 class genesis
 {
 public:
```
