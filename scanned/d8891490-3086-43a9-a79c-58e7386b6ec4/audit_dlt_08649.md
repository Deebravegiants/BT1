# [?] Merge pull request #2240 from DanShaders/simplex-dos-hardening

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2026-03-27
Source: https://github.com/ton-blockchain/ton/commit/b35dd0beb6126e42f0a8a05a24a441adf37c863a
Type: security-commit

## Details
Merge pull request #2240 from DanShaders/simplex-dos-hardening

Simplex DoS hardening

## Patch
### crypto/block/block.tlb
```diff
@@ -782,6 +782,7 @@ _ ConsensusConfig = ConfigParam 29;
 simplex_config#21 flags:(## 7) use_quic:Bool
   target_rate_ms:uint32 slots_per_leader_window:uint32
   first_block_timeout_ms:uint32 max_leader_window_desync:uint32 = NewConsensusConfig;
+simplex_config_v2#22 flags:(## 7) use_quic:Bool slots_per_leader_window:uint32 noncritical_params:(HashmapE 8 uint32) = NewConsensusConfig;
 new_consensus_config_all#10 mc:(Maybe ^NewConsensusConfig) shard:(Maybe ^NewConsensusConfig) = NewConsensusConfigAll;
 _ NewConsensusConfigAll = ConfigParam 30;
 
```

### crypto/block/mc-config.cpp
```diff
@@ -361,6 +361,28 @@ ton::ValidatorSessionConfig Config::get_consensus_config() const {
   return c;
 }
 
+namespace {
+
+template <typename Base, td::uint32(Base::* where)>
+void store_uint32(Base& base, td::uint32 value) {
+  base.*where = value;
+}
+
+template <typename Base, std::chrono::milliseconds(Base::* where)>
+void store_milliseconds(Base& base, td::uint32 value) {
+  base.*where = std::chrono::milliseconds{value};
+}
+
+template <typename Base, double(Base::* where)>
+void store_double(Base& base, td::uint32 value) {
+  float fvalue;
+  static_assert(sizeof(float) == sizeof(td::uint32));
+  memcpy(&fvalue, &value, sizeof(float));
+  base.*where = fvalue;
+}
+
+}  // namespace
+
 td::optional<ton::NewConsensusConfig> Config::get_new_consensus_config(ton::WorkchainId wc) const {
   auto c1 = get_config_param(30);
   if (c1.is_null()) {
@@ -375,17 +397,54 @@ td::optional<ton::NewConsensusConfig> Config::get_new_consensus_config(ton::Work
     return {};
   }
   auto consensus_config = get_consensus_config();
-  gen::NewConsensusConfig::Record r2;
-  if (gen::unpack_cell(c2, r2)) {
+
+  if (gen::NewConsensusConfig::Record_simplex_config v1; gen::unpack_cell(c2, v1)) {
     return ton::NewConsensusConfig{
-        .target_rate_ms = r2.target_rate_ms,
         .max_block_size = consensus_config.max_block_size,
         .max_collated_data_size = consensus_config.max_collated_data_size,
-        .use_quic = r2.use_quic,
-        .consensus = ton::NewConsensusConfig::Simplex{.slots_per_leader_window = r2.slots_per_leader_window,
-                                                      .first_block_timeout_ms = r2.first_block_timeout_ms,
-                                                      .max_leader_window_desync = r2.max_leader_window_desync}};
+
+        .use_quic = v1.use_quic,
+        .slots_per_leader_window = v1.slots_per_leader_window,
+
+        .noncritical_params =
+            {
+                .target_rate{v1.target_rate_ms},
+                .first_block_timeout{v1.first_block_timeout_ms},
+                .max_leader_window_desync = v1.max_leader_window_desync,
+            },
+    };
+  } else if (gen::NewConsensusConfig::Record_simplex_config_v2 v2; gen::unpack_cell(c2, v2)) {
+    ton::NewConsensusConfig config{
+        .max_block_size = consensus_config.max_block_size,
+        .max_collated_data_size = consensus_config.max_collated_data_size,
+
+        .use_quic = v2.use_quic,
+        .slots_per_leader_window = v2.slots_per_leader_window,
+    };
+
+    using NoncriticalParams = ton::NewConsensusConfig::NoncriticalParams;
+
+    static constexpr auto mapping = std::to_array({
+#define READ_UINT32(idx, name, _) std::pair{idx, &store_uint32<NoncriticalParams, &NoncriticalParams::name>},
+#define READ_DOUBLE(idx, name, _) std::pair{idx, &store_double<NoncriticalParams, &NoncriticalParams::name>},
+#define READ_DURATION(idx, name, _) std::pair{idx, &store_milliseconds<NoncriticalParams, &NoncriticalParams::name>},
+        ENUMERATE_NONCRITICAL_PARAMS(READ_UINT32, READ_DOUBLE, READ_DURATION)
+#undef READ_UINT32
+#undef READ_DOUBLE
+#undef READ_DURATION
+    });
+
+    vm::DictionaryFixed params{v2.noncritical_params, 8};
+    for (const auto& [key, store_func] : mapping) {
+      if (auto param = params.lookup(td::BitArray<8>(key)); param.not_null()) {
+        auto val = td::narrow_cast<td::uint32>(param->prefetch_ulong(32));
+        store_func(config.noncritical_params, val);
+      }
+    }
+
+    return config;
   }
+
   return {};
 }
 
```

### overlay/overlay-manager.cpp
```diff
@@ -289,7 +289,7 @@ void OverlayManager::receive_message(adnl::AdnlNodeIdShort src, adnl::AdnlNodeId
     VLOG(OVERLAY_NOTICE) << this << ": message to localid is not in overlay " << overlay_id << "@" << dst;
 
     if (buffer_limits_.max_packets != 0 && buffer_limits_.max_data_size >= data.size()) {
-      while (buffered_requests_.total_packets > buffer_limits_.max_packets ||
+      while (buffered_requests_.total_packets >= buffer_limits_.max_packets ||
              buffered_requests_.total_data_size + data.size() > buffer_limits_.max_data_size) {
         buffered_requests_.evict_oldest();
       }
@@ -336,7 +336,7 @@ void OverlayManager::receive_query(adnl::AdnlNodeIdShort src, adnl::AdnlNodeIdSh
     VLOG(OVERLAY_NOTICE) << this << ": query to localid not in overlay " << overlay_id << "@" << dst << " from " << src;
 
     if (buffer_limits_.max_packets != 0 && buffer_limits_.max_data_size >= data.size()) {
-      while (buffered_requests_.total_packets > buffer_limits_.max_packets ||
+      while (buffered_requests_.total_packets >= buffer_limits_.max_packets ||
              buffered_requests_.total_data_size + data.size() > buffer_limits_.max_data_size) {
         buffered_requests_.evict_oldest();
       }
```

### tdutils/td/utils/Time.h
```diff
@@ -18,6 +18,8 @@
 */
 #pragma once
 
+#include <chrono>
+
 #include "td/utils/common.h"
 #include "td/utils/port/Clocks.h"
 
@@ -74,6 +76,10 @@ class Timestamp {
     return Timestamp{timeout - Clocks::system() + Time::now()};
   }
 
+  static Timestamp in(std::chrono::duration<double> timeout, td::Timestamp now = td::Timestamp::now_cached()) {
+    return Timestamp{now.at() + timeout.count()};
+  }
+
   static Timestamp in(double timeout, td::Timestamp now = td::Timestamp::now_cached()) {
     return Timestamp{now.at() + timeout};
   }
@@ -128,6 +134,10 @@ inline Timestamp &operator+=(Timestamp &a, double b) {
   return a;
 }
 
+inline Timestamp operator+(Timestamp a, std::chrono::duration<double> b) {
+  return Timestamp::at(a.at() + b.count());
+}
+
 inline double operator-(const Timestamp &a, const Timestamp &b) {
   return a.at() - b.at();
 }
```

### test/CMakeLists.txt
```diff
@@ -3,4 +3,4 @@ target_link_libraries(td-test-main PRIVATE tdutils)
 
 add_subdirectory(tdactor)
 add_subdirectory(tonlib)
-add_subdirectory(consensus)
+add_subdirectory(validator)
```

### test/consensus/CMakeLists.txt
```diff
@@ -1,3 +0,0 @@
-add_executable(test-consensus test-consensus.cpp)
-target_link_libraries(test-consensus overlay tdutils tdactor adnl adnltest rldp tl_api dht validator ton_validator validator)
-# add_test(test-consensus test-consensus)
```

### test/tontester/src/tonlib/engine_console.py
```diff
@@ -86,3 +86,15 @@ async def request(self, request: TLRequest) -> JSONSerializable:
     async def get_actor_stats(self) -> str:
         query = ton_api.Engine_validator_getActorTextStatsRequest()
         return query.parse_result(await self.request(query)).data
+
+    async def get_consensus_noncritical_params_overrides(
+        self,
+    ) -> ton_api.Consensus_noncriticalParamsOverrideList:
+        query = ton_api.Engine_validator_getConsensusNoncriticalParamsOverridesRequest()
+        return query.parse_result(await self.request(query))
+
+    async def set_consensus_noncritical_params_overrides(
+        self, overrides: ton_api.Consensus_noncriticalParamsOverrideList
+    ) -> None:
+        query = ton_api.Engine_validator_setConsensusNoncriticalParamsOverridesRequest(overrides)
+        _ = await self.request(query)
```

### test/validator/CMakeLists.txt
```diff
@@ -0,0 +1 @@
+add_subdirectory(consensus)
```

### test/validator/consensus/CMakeLists.txt
```diff
@@ -0,0 +1,13 @@
+add_executable(test-consensus test-consensus.cpp)
+target_link_libraries(test-consensus PRIVATE
+    adnl
+    adnltest
+    dht
+    overlay
+    rldp
+    tdactor
+    tdutils
+    tl_api
+    ton_validator
+    validator
+)
```

### test/validator/consensus/test-consensus.cpp
```diff
@@ -680,11 +680,11 @@ class TestConsensus : public td::actor::Actor {
     bus->total_weight = total_weight_;
     bus->local_id = validators_[node_idx];
     bus->config = NewConsensusConfig{
-        .target_rate_ms = TARGET_RATE_MS,
         .max_block_size = 1 << 20,
         .max_collated_data_size = 1 << 20,
-        .consensus = NewConsensusConfig::Simplex{.slots_per_leader_window = SLOTS_PER_LEADER_WINDOW}};
-    bus->simplex_config = bus->config.consensus;
+        .slots_per_leader_window = SLOTS_PER_LEADER_WINDOW,
+        .noncritical_params = {.target_rate{TARGET_RATE_MS}},
+    };
     bus->session_id = SESSION_ID;
     bus->cc_seqno = CC_SEQNO;
     bus->validator_set_hash = validator_set_->get_validator_set_hash();
@@ -694,7 +694,8 @@ class TestConsensus : public td::actor::Actor {
                              PSTRING() << "consensus." << node_idx << "." << instance_idx);
     inst.status = Instance::Running;
     inst.bus.publish<BlockFinalizedInMasterchain>(last_accepted_block_);
-    inst.bus.publish<Start>(ChainState::from_zerostate(FIRST_PARENT, gen_shard_state(0), MIN_MC_BLOCK_ID));
+    inst.bus.publish<Start>(
+        td::make_ref<ChainState>(ChainState::ZerostateTip{FIRST_PARENT, gen_shard_state(0)}, MIN_MC_BLOCK_ID));
     LOG(ERROR) << "Starting node #" << node_idx << "." << instance_idx;
   }
 
```

### tl/generate/scheme/ton_api.tl
```diff
@@ -1237,5 +1237,37 @@ consensus.stats.events id:int256 events:(vector consensus.stats.timestampedEvent
 consensus.simplex.stats.voted vote:consensus.simplex.UnsignedVote = consensus.stats.Event;
 consensus.simplex.stats.certObserved vote:consensus.simplex.UnsignedVote = consensus.stats.Event;
 
+consensus.simplex.noncriticalParams
+    flags:#
+    target_rate_ms:flags.0?int
+    first_block_timeout_ms:flags.1?int
+    first_block_timeout_multiplier:flags.2?double
+    first_block_timeout_cap_ms:flags.3?int
+    candidate_resolve_timeout_ms:flags.4?int
+    candidate_resolve_timeout_multiplier:flags.5?double
+    candidate_resolve_timeout_cap_ms:flags.6?int
+    candidate_resolve_cooldown_ms:flags.7?int
+    standstill_timeout_ms:flags.8?int
+    standstill_max_egress_bytes_per_s:flags.9?int
+    max_leader_window_desync:flags.10?int
+    bad_signature_ban_duration_ms:flags.11?int
+    candidate_resolve_rate_limit:flags.12?int
+    = consensus.NoncriticalParams;
+
+consensus.noncriticalParamsOverride
+    workchain:int
+    shard:long
+    from_seqno:int
+    to_seqno:int
+    override:consensus.NoncriticalParams
+    = consensus.NoncriticalParamsOverride;
+
+consensus.noncriticalParamsOverrideList
+    overrides:(vector consensus.noncriticalParamsOverride)
+    = consensus.NoncriticalParamsOverrideList;
+
 ---functions---
 consensus.simplex.requestCandidate id:consensus.CandidateId want_candidate:Bool want_notar:Bool = consensus.simplex.CandidateAndCert;
+
+engine.validator.setConsensusNoncriticalParamsOverrides overrides:consensus.noncriticalParamsOverrideList = engine.validator.Success;
+engine.validator.getConsensusNoncriticalParamsOverrides = consensus.NoncriticalParamsOverrideList;
```

### ton/ton-types.h
```diff
@@ -18,6 +18,7 @@
 */
 #pragma once
 
+#include <chrono>
 #include <cinttypes>
 
 #include "crypto/common/bitstring.h"
@@ -534,17 +535,42 @@ struct ValidatorSessionConfig {
 };
 
 struct NewConsensusConfig {
-  td::uint32 target_rate_ms = 1000;
   td::uint32 max_block_size = (4 << 20);
   td::uint32 max_collated_data_size = (4 << 20);
-  bool use_quic = false;
 
-  struct Simplex {
-    td::uint32 slots_per_leader_window = 4;
-    td::uint32 first_block_timeout_ms = 1000;
-    td::uint32 max_leader_window_desync = 2;
+  bool use_quic = false;
+  td::uint32 slots_per_leader_window = 4;
+
+  // clang-format off
+#define ENUMERATE_NONCRITICAL_PARAMS(uint32_fn, double_fn, duration_fn) \
+  duration_fn(0, target_rate, 2'400)                                    \
+  duration_fn(1, first_block_timeout, 1'000)                            \
+  double_fn(2, first_block_timeout_multiplier, 1.2)                     \
+  duration_fn(3, first_block_timeout_cap, 100'000)                      \
+  duration_fn(4, candidate_resolve_timeout, 1'000)                      \
+  double_fn(5, candidate_resolve_timeout_multiplier, 1.2)               \
+  duration_fn(6, candidate_resolve_timeout_cap, 10'000)                 \
+  duration_fn(7, candidate_resolve_cooldown, 10)                        \
+  duration_fn(8, standstill_timeout, 10'000)                            \
+  uint32_fn(9, standstill_max_egress_bytes_per_s, 50 << 17)             \
+  uint32_fn(10, max_leader_window_desync, 250)                          \
+  duration_fn(11, bad_signature_ban_duration, 5'000)                    \
+  uint32_fn(12, candidate_resolve_rate_limit, 10)
+  // clang-format on
+
+  struct NoncriticalParams {
+#define DEFINE_UINT32_FIELD(_, name, value) td::uint32 name = value;
+#define DEFINE_DOUBLE_FIELD(_, name, value) double name = value;
+#define DEFINE_DURATION_FIELD(_, name, value) std::chrono::milliseconds name{value};
+    ENUMERATE_NONCRITICAL_PARAMS(DEFINE_UINT32_FIELD, DEFINE_DOUBLE_FIELD, DEFINE_DURATION_FIELD)
+#undef DEFINE_UINT32_FIELD
+#undef DEFINE_DOUBLE_FIELD
+#undef DEFINE_DURATION_FIELD
+
+    bool operator==(const NoncriticalParams&) const = default;
   };
-  Simplex consensus;
+
+  NoncriticalParams noncritical_params = {};
 };
 
 struct PersistentStateDescription : public td::CntObject {
```
