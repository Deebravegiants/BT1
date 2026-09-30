# [?] Fix archive-ttl overflow, remove unused code, clarify validator-engine flags (#1605)

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2025-04-05
Source: https://github.com/ton-blockchain/ton/commit/5661301db5c0d7a6facea4906fe160c9802bf655
Type: security-commit

## Details
Fix archive-ttl overflow, remove unused code, clarify validator-engine flags (#1605)

## Patch
### validator-engine/validator-engine.cpp
```diff
@@ -4359,7 +4359,7 @@ int main(int argc, char *argv[]) {
     acts.push_back([&x, v]() { td::actor::send_closure(x, &ValidatorEngine::set_max_mempool_num, v); });
     return td::Status::OK();
   });
-  p.add_checked_option('b', "block-ttl", "blocks will be gc'd after this time (in seconds) default=86400",
+  p.add_checked_option('b', "block-ttl", "deprecated",
                        [&](td::Slice fname) {
                          auto v = td::to_double(fname);
                          if (v <= 0) {
@@ -4369,7 +4369,9 @@ int main(int argc, char *argv[]) {
                          return td::Status::OK();
                        });
   p.add_checked_option(
-      'A', "archive-ttl", "archived blocks will be deleted after this time (in seconds) default=7*86400",
+      'A', "archive-ttl",
+      "ttl for archived blocks (in seconds) default=7*86400. Note: archived blocks are gc'd after state-ttl + "
+      "archive-ttl seconds",
       [&](td::Slice fname) {
         auto v = td::to_double(fname);
         if (v <= 0) {
@@ -4379,7 +4381,7 @@ int main(int argc, char *argv[]) {
         return td::Status::OK();
       });
   p.add_checked_option(
-      'K', "key-proof-ttl", "key blocks will be deleted after this time (in seconds) default=365*86400*10",
+      'K', "key-proof-ttl", "deprecated",
       [&](td::Slice fname) {
         auto v = td::to_double(fname);
         if (v <= 0) {
```

### validator/db/archive-manager.cpp
```diff
@@ -965,8 +965,8 @@ void ArchiveManager::alarm() {
   }
 }
 
-void ArchiveManager::run_gc(UnixTime mc_ts, UnixTime gc_ts, UnixTime archive_ttl) {
-  auto p = get_temp_package_id_by_unixtime(mc_ts - TEMP_PACKAGES_TTL);
+void ArchiveManager::run_gc(UnixTime mc_ts, UnixTime gc_ts, double archive_ttl) {
+  auto p = get_temp_package_id_by_unixtime((double)mc_ts - TEMP_PACKAGES_TTL);
   std::vector<PackageId> vec;
   for (auto &x : temp_files_) {
     if (x.first < p) {
@@ -994,7 +994,7 @@ void ArchiveManager::run_gc(UnixTime mc_ts, UnixTime gc_ts, UnixTime archive_ttl
       if (it == desc.first_blocks.end()) {
         continue;
       }
-      if (it->second.ts < gc_ts - archive_ttl) {
+      if ((double)it->second.ts < (double)gc_ts - archive_ttl) {
         vec.push_back(f.first);
       }
     }
```

### validator/db/archive-manager.hpp
```diff
@@ -61,7 +61,7 @@ class ArchiveManager : public td::actor::Actor {
   void truncate(BlockSeqno masterchain_seqno, ConstBlockHandle handle, td::Promise<td::Unit> promise);
   //void truncate_continue(BlockSeqno masterchain_seqno, td::Promise<td::Unit> promise);
 
-  void run_gc(UnixTime mc_ts, UnixTime gc_ts, UnixTime archive_ttl);
+  void run_gc(UnixTime mc_ts, UnixTime gc_ts, double archive_ttl);
 
   /* from LTDB */
   void get_block_by_unix_time(AccountIdPrefixFull account_id, UnixTime ts, td::Promise<ConstBlockHandle> promise);
@@ -240,7 +240,7 @@ class ArchiveManager : public td::actor::Actor {
 
   void update_permanent_slices();
 
-  static const td::uint32 TEMP_PACKAGES_TTL = 3600;
+  static constexpr double TEMP_PACKAGES_TTL = 3600;
 };
 
 }  // namespace validator
```

### validator/db/rootdb.cpp
```diff
@@ -431,10 +431,6 @@ void RootDb::allow_state_gc(BlockIdExt block_id, td::Promise<bool> promise) {
   td::actor::send_closure(validator_manager_, &ValidatorManager::allow_block_state_gc, block_id, std::move(promise));
 }
 
-void RootDb::allow_block_gc(BlockIdExt block_id, td::Promise<bool> promise) {
-  td::actor::send_closure(validator_manager_, &ValidatorManager::allow_block_info_gc, block_id, std::move(promise));
-}
-
 void RootDb::prepare_stats(td::Promise<std::vector<std::pair<std::string, std::string>>> promise) {
   auto merger = StatsMerger::create(std::move(promise));
   td::actor::send_closure(cell_db_, &CellDb::prepare_stats, merger.make_promise("celldb."));
@@ -519,7 +515,7 @@ void RootDb::set_async_mode(bool mode, td::Promise<td::Unit> promise) {
   td::actor::send_closure(archive_db_, &ArchiveManager::set_async_mode, mode, std::move(promise));
 }
 
-void RootDb::run_gc(UnixTime mc_ts, UnixTime gc_ts, UnixTime archive_ttl) {
+void RootDb::run_gc(UnixTime mc_ts, UnixTime gc_ts, double archive_ttl) {
   td::actor::send_closure(archive_db_, &ArchiveManager::run_gc, mc_ts, gc_ts, archive_ttl);
 }
 
```

### validator/db/rootdb.hpp
```diff
@@ -118,8 +118,6 @@ class RootDb : public Db {
   void archive(BlockHandle handle, td::Promise<td::Unit> promise) override;
 
   void allow_state_gc(BlockIdExt block_id, td::Promise<bool> promise);
-  void allow_block_gc(BlockIdExt block_id, td::Promise<bool> promise);
-  //void allow_gc(FileDb::RefId ref_id, bool is_archive, td::Promise<bool> promise);
 
   void prepare_stats(td::Promise<std::vector<std::pair<std::string, std::string>>> promise) override;
 
@@ -137,7 +135,7 @@ class RootDb : public Db {
                          td::Promise<td::BufferSlice> promise) override;
   void set_async_mode(bool mode, td::Promise<td::Unit> promise) override;
 
-  void run_gc(UnixTime mc_ts, UnixTime gc_ts, UnixTime archive_ttl) override;
+  void run_gc(UnixTime mc_ts, UnixTime gc_ts, double archive_ttl) override;
   void add_persistent_state_description(td::Ref<PersistentStateDescription> desc, td::Promise<td::Unit> promise) override;
   void get_persistent_state_descriptions(td::Promise<std::vector<td::Ref<PersistentStateDescription>>> promise) override;
 
```

### validator/interfaces/db.h
```diff
@@ -123,7 +123,7 @@ class Db : public td::actor::Actor {
                                  td::Promise<td::BufferSlice> promise) = 0;
   virtual void set_async_mode(bool mode, td::Promise<td::Unit> promise) = 0;
 
-  virtual void run_gc(UnixTime mc_ts, UnixTime gc_ts, UnixTime archive_ttl) = 0;
+  virtual void run_gc(UnixTime mc_ts, UnixTime gc_ts, double archive_ttl) = 0;
 
   virtual void add_persistent_state_description(td::Ref<PersistentStateDescription> desc,
                                                 td::Promise<td::Unit> promise) = 0;
```

### validator/interfaces/validator-manager.h
```diff
@@ -160,16 +160,7 @@ class ValidatorManager : public ValidatorManagerInterface {
 
   virtual void try_get_static_file(FileHash file_hash, td::Promise<td::BufferSlice> promise) = 0;
 
-  virtual void allow_block_data_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) = 0;
   virtual void allow_block_state_gc(BlockIdExt block_id, td::Promise<bool> promise) = 0;
-  virtual void allow_zero_state_file_gc(BlockIdExt block_id, td::Promise<bool> promise) = 0;
-  virtual void allow_persistent_state_file_gc(BlockIdExt block_id, BlockIdExt masterchain_block_id,
-                                              td::Promise<bool> promise) = 0;
-  virtual void allow_block_signatures_gc(BlockIdExt block_id, td::Promise<bool> promise) = 0;
-  virtual void allow_block_proof_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) = 0;
-  virtual void allow_block_proof_link_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) = 0;
-  virtual void allow_block_candidate_gc(BlockIdExt block_id, td::Promise<bool> promise) = 0;
-  virtual void allow_block_info_gc(BlockIdExt block_id, td::Promise<bool> promise) = 0;
 
   virtual void archive(BlockHandle handle, td::Promise<td::Unit> promise) = 0;
 
```

### validator/manager-disk.hpp
```diff
@@ -341,34 +341,9 @@ class ValidatorManagerImpl : public ValidatorManager {
   void update_gc_block_handle(BlockHandle handle, td::Promise<td::Unit> promise) override {
     promise.set_value(td::Unit());
   }
-  void allow_block_data_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
   void allow_block_state_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
     promise.set_result(false);
   }
-  void allow_zero_state_file_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_persistent_state_file_gc(BlockIdExt block_id, BlockIdExt masterchain_block_id,
-                                      td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_signatures_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_proof_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_proof_link_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_candidate_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_info_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
   void archive(BlockHandle handle, td::Promise<td::Unit> promise) override {
     td::actor::send_closure(db_, &Db::archive, std::move(handle), std::move(promise));
   }
```

### validator/manager-hardfork.hpp
```diff
@@ -406,34 +406,9 @@ class ValidatorManagerImpl : public ValidatorManager {
   void update_gc_block_handle(BlockHandle handle, td::Promise<td::Unit> promise) override {
     promise.set_value(td::Unit());
   }
-  void allow_block_data_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
   void allow_block_state_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
     promise.set_result(false);
   }
-  void allow_zero_state_file_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_persistent_state_file_gc(BlockIdExt block_id, BlockIdExt masterchain_block_id,
-                                      td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_signatures_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_proof_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_proof_link_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_candidate_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_block_info_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
   void archive(BlockHandle handle, td::Promise<td::Unit> promise) override {
     UNREACHABLE();
   }
```

### validator/manager.cpp
```diff
@@ -2374,7 +2374,7 @@ void ValidatorManagerImpl::try_advance_gc_masterchain_block() {
       gc_masterchain_handle_->id().id.seqno < last_masterchain_state_->last_key_block_id().seqno() &&
       gc_masterchain_handle_->id().id.seqno < min_confirmed_masterchain_seqno_ &&
       gc_masterchain_handle_->id().id.seqno < state_serializer_masterchain_seqno_ &&
-      gc_masterchain_state_->get_unix_time() < td::Clocks::system() - state_ttl()) {
+      (double)gc_masterchain_state_->get_unix_time() < td::Clocks::system() - state_ttl()) {
     gc_advancing_ = true;
     auto block_id = gc_masterchain_handle_->one_next(true);
 
@@ -2386,100 +2386,6 @@ void ValidatorManagerImpl::try_advance_gc_masterchain_block() {
   }
 }
 
-void ValidatorManagerImpl::allow_persistent_state_file_gc(BlockIdExt block_id, BlockIdExt masterchain_block_id,
-                                                          td::Promise<bool> promise) {
-  if (!gc_masterchain_handle_) {
-    promise.set_result(false);
-    return;
-  }
-  if (masterchain_block_id.seqno() == 0) {
-    promise.set_result(false);
-    return;
-  }
-  if (masterchain_block_id.seqno() >= gc_masterchain_handle_->id().seqno()) {
-    promise.set_result(false);
-    return;
-  }
-  auto P = td::PromiseCreator::lambda([promise = std::move(promise)](td::Result<BlockHandle> R) mutable {
-    R.ensure();
-    auto handle = R.move_as_ok();
-    CHECK(handle->is_key_block());
-    promise.set_result(ValidatorManager::persistent_state_ttl(handle->unix_time()) < td::Clocks::system());
-  });
-  get_block_handle(masterchain_block_id, false, std::move(P));
-}
-
-void ValidatorManagerImpl::allow_archive(BlockIdExt block_id, td::Promise<bool> promise) {
-  /*if (!gc_masterchain_handle_) {
-    promise.set_result(false);
-    return;
-  }
-  if (!block_id.is_masterchain()) {
-    if (!gc_masterchain_state_->workchain_is_active(block_id.id.workchain)) {
-      promise.set_result(false);
-      return;
-    }
-    bool found = false;
-    auto S = gc_masterchain_state_->get_shard_from_config(block_id.shard_full());
-    if (S.not_null()) {
-      if (block_id.id.seqno >= S->top_block_id().id.seqno) {
-        promise.set_result(false);
-        return;
-      }
-      found = true;
-    } else {
-      auto shards = gc_masterchain_state_->get_shards();
-      for (auto shard : shards) {
-        if (shard_intersects(shard->shard(), block_id.shard_full())) {
-          if (block_id.id.seqno >= shard->top_block_id().id.seqno) {
-            promise.set_result(false);
-            return;
-          }
-          found = true;
-        }
-      }
-    }
-    CHECK(found);
-  } else {
-    if (block_id.id.seqno >= gc_masterchain_handle_->id().id.seqno) {
-      promise.set_result(false);
-      return;
-    }
-  }
-  auto P = td::PromiseCreator::lambda([promise = std::move(promise)](td::Result<td::Unit> R) mutable {
-    if (R.is_error()) {
-      promise.set_error(R.move_as_error());
-    } else {
-      promise.set_result(true);
-    }
-  });
-  td::actor::send_closure(db_, &Db::archive, block_id, std::move(P));*/
-  promise.set_result(false);
-}
-
-void ValidatorManagerImpl::allow_delete(BlockIdExt block_id, td::Promise<bool> promise) {
-  auto key_ttl = td::Clocks::system() - opts_->key_proof_ttl();
-  auto ttl = td::Clocks::system() - opts_->archive_ttl();
-  auto P = td::PromiseCreator::lambda(
-      [SelfId = actor_id(this), promise = std::move(promise), ttl, key_ttl](td::Result<BlockHandle> R) mutable {
-        if (R.is_error()) {
-          promise.set_result(true);
-          return;
-        }
-        auto handle = R.move_as_ok();
-        if (!handle->inited_unix_time()) {
-          promise.set_result(true);
-          return;
-        }
-        if (!handle->inited_is_key_block() || !handle->is_key_block()) {
-          promise.set_result(handle->unix_time() <= ttl);
-        } else {
-          promise.set_result(handle->unix_time() <= key_ttl);
-        }
-      });
-  get_block_handle(block_id, false, std::move(P));
-}
-
 void ValidatorManagerImpl::allow_block_state_gc(BlockIdExt block_id, td::Promise<bool> promise) {
   if (!gc_masterchain_handle_) {
     promise.set_result(false);
@@ -2508,27 +2414,6 @@ void ValidatorManagerImpl::allow_block_state_gc(BlockIdExt block_id, td::Promise
   UNREACHABLE();
 }
 
-void ValidatorManagerImpl::allow_block_info_gc(BlockIdExt block_id, td::Promise<bool> promise) {
-  auto P =
-      td::PromiseCreator::lambda([db = db_.get(), promise = std::move(promise)](td::Result<BlockHandle> R) mutable {
-        if (R.is_error()) {
-          promise.set_result(false);
-        } else {
-          auto handle = R.move_as_ok();
-          if (!handle->moved_to_archive() || !handle->is_applied()) {
-            promise.set_result(false);
-          } else {
-            auto P = td::PromiseCreator::lambda([promise = std::move(promise)](td::Result<td::Unit> R) mutable {
-              R.ensure();
-              promise.set_result(true);
-            });
-            td::actor::send_closure(db, &Db::store_block_handle, handle, std::move(P));
-          }
-        }
-      });
-  get_block_handle(block_id, false, std::move(P));
-}
-
 void ValidatorManagerImpl::got_next_gc_masterchain_handle(BlockHandle handle) {
   CHECK(gc_advancing_);
   auto P = td::PromiseCreator::lambda([SelfId = actor_id(this), handle](td::Result<td::Ref<ShardState>> R) {
@@ -2610,7 +2495,7 @@ void ValidatorManagerImpl::alarm() {
   alarm_timestamp() = td::Timestamp::in(1.0);
   if (shard_client_handle_ && gc_masterchain_handle_) {
     td::actor::send_closure(db_, &Db::run_gc, shard_client_handle_->unix_time(), gc_masterchain_handle_->unix_time(),
-                            static_cast<UnixTime>(opts_->archive_ttl()));
+                            opts_->archive_ttl());
   }
   if (log_status_at_.is_in_past()) {
     if (last_masterchain_block_handle_) {
```

### validator/manager.hpp
```diff
@@ -568,30 +568,7 @@ class ValidatorManagerImpl : public ValidatorManager {
   }
 
  public:
-  void allow_delete(BlockIdExt block_id, td::Promise<bool> promise);
-  void allow_archive(BlockIdExt block_id, td::Promise<bool> promise);
-  void allow_block_data_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    allow_archive(block_id, std::move(promise));
-  }
   void allow_block_state_gc(BlockIdExt block_id, td::Promise<bool> promise) override;
-  void allow_zero_state_file_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    promise.set_result(false);
-  }
-  void allow_persistent_state_file_gc(BlockIdExt block_id, BlockIdExt masterchain_block_id,
-                                      td::Promise<bool> promise) override;
-  void allow_block_signatures_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    allow_archive(block_id, std::move(promise));
-  }
-  void allow_block_proof_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    allow_archive(block_id, std::move(promise));
-  }
-  void allow_block_proof_link_gc(BlockIdExt block_id, bool is_archive, td::Promise<bool> promise) override {
-    allow_archive(block_id, std::move(promise));
-  }
-  void allow_block_candidate_gc(BlockIdExt block_id, td::Promise<bool> promise) override {
-    allow_block_state_gc(block_id, std::move(promise));
-  }
-  void allow_block_info_gc(BlockIdExt block_id, td::Promise<bool> promise) override;
   void archive(BlockHandle handle, td::Promise<td::Unit> promise) override {
     td::actor::send_closure(db_, &Db::archive, std::move(handle), std::move(promise));
   }
@@ -716,9 +693,6 @@ class ValidatorManagerImpl : public ValidatorManager {
   double state_ttl() const {
     return opts_->state_ttl();
   }
-  double block_ttl() const {
-    return opts_->block_ttl();
-  }
   double max_mempool_num() const {
     return opts_->max_mempool_num();
   }
```
