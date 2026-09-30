# [?] db_lmdb: fix race crash using a stale cursor

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2020-03-12
Source: https://github.com/monero-project/monero/commit/ec010777205d923828cf22a59a8f2978210d75a4
Type: security-commit

## Details
db_lmdb: fix race crash using a stale cursor

If a db resize happened, the txpool meta cursor might be stale,
and was not being renewed when necessary.
It would cause this SEGSEGV:

in mdb_cursor_set ()
in mdb_cursor_get ()
in cryptonote::BlockchainLMDB::get_txpool_tx_blob(crypto::hash const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&, cryptonote::relay_category) const ()
in cryptonote::tx_memory_pool::get_transaction(crypto::hash const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&, cryptonote::relay_category) const ()
in cryptonote::t_cryptonote_protocol_handler<cryptonote::core>::handle_notify_new_fluffy_block(int, epee::misc_utils::struct_init<cryptonote::NOTIFY_NEW_FLUFFY_BLOCK::request_t>&, cryptonote::cryptonote_connection_context&) ()

## Patch
### src/blockchain_db/lmdb/db_lmdb.cpp
```diff
@@ -1915,6 +1915,7 @@ bool BlockchainLMDB::get_txpool_tx_blob(const crypto::hash& txid, cryptonote::bl
   // if filtering, make sure those requirements are met before copying blob
   if (tx_category != relay_category::all)
   {
+    RCURSOR(txpool_meta)
     auto result = mdb_cursor_get(m_cur_txpool_meta, &k, &v, MDB_SET);
     if (result == MDB_NOTFOUND)
       return false;
```
