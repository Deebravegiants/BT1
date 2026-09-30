# [?] Invent "noncritical params" for Simplex timing & DoS protection params

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2026-03-25
Source: https://github.com/ton-blockchain/ton/commit/2e4585f5045c1993e02c482d3bb768a9ce04e688
Type: security-commit

## Details
Invent "noncritical params" for Simplex timing & DoS protection params

The idea is to allow overriding these parameters from the engine console
if we need to do a manual recovery.

The commit allows these noncritical parameters to be set from config (we
expect to use this mainly for target_block_rate) and from validator
options.

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

### test/consensus/test-consensus.cpp
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

### validator/consensus/block-producer.cpp
```diff
@@ -20,7 +20,12 @@ class BlockProducerImpl : public td::actor::SpawnsWith<Bus>, public td::actor::C
   TON_RUNTIME_DEFINE_EVENT_HANDLER();
 
   void start_up() {
-    target_rate_ = owning_bus()->config.target_rate_ms / 1000.;
+    target_rate_ = owning_bus()->config.noncritical_params.target_rate;
+  }
+
+  template <>
+  void handle(BusHandle, std::shared_ptr<const NoncriticalParamsUpdated> event) {
+    target_rate_ = event->params.target_rate;
   }
 
   template <>
@@ -170,7 +175,7 @@ class BlockProducerImpl : public td::actor::SpawnsWith<Bus>, public td::actor::C
 
   BlockSeqno last_consensus_finalized_seqno_ = 0;
   BlockSeqno last_mc_finalized_seqno_ = 0;
-  double target_rate_;
+  std::chrono::milliseconds target_rate_;
 };
 
 }  // namespace
```

### validator/consensus/bridge.cpp
```diff
@@ -190,6 +190,13 @@ class BridgeImpl final : public IValidatorGroup {
       LOG(WARNING) << "Accelerator is not consistently supported with simplex consensus";
     }
     td::actor::send_closure(manager_facade_, &ManagerFacadeImpl::update_collator_options, opts);
+
+    auto new_noncritical_params =
+        opts->get_noncritical_params(bus_->shard, bus_->cc_seqno, bus_->config.noncritical_params);
+    if (current_noncritical_params_ != new_noncritical_params) {
+      bus_.publish<NoncriticalParamsUpdated>(new_noncritical_params);
+      current_noncritical_params_ = new_noncritical_params;
+    }
   }
 
   virtual void get_validator_group_info_for_litequery(
@@ -213,9 +220,7 @@ class BridgeImpl final : public IValidatorGroup {
                                                                  params_.collation_manager, params_.validator_set,
                                                                  params_.validator_opts);
 
-    auto simplex_bus = std::make_shared<simplex::Bus>();
-    simplex_bus->simplex_config = params_.config.consensus;
-    std::shared_ptr<Bus> bus = simplex_bus;
+    auto bus = std::make_shared<simplex::Bus>();
 
     bus->shard = params_.shard;
     bus->manager = manager_facade_.get();
@@ -251,6 +256,9 @@ class BridgeImpl final : public IValidatorGroup {
     CHECK(found);
 
     bus->config = std::move(params_.config);
+    bus->config.noncritical_params =
+        params_.validator_opts->get_noncritical_params(bus->shard, bus->cc_seqno, bus->config.noncritical_params);
+    current_noncritical_params_ = bus->config.noncritical_params;
 
     bus->session_id = params_.session_id;
     bus->overlays = params_.overlays;
@@ -278,7 +286,7 @@ class BridgeImpl final : public IValidatorGroup {
     simplex::StateResolver::register_in(runtime);
     simplex::MetricCollector::register_in(runtime);
 
-    bus_ = runtime.start(simplex_bus, params_.name);
+    bus_ = runtime.start(bus, params_.name);
   }
 
  private:
@@ -329,6 +337,8 @@ class BridgeImpl final : public IValidatorGroup {
 
   std::shared_ptr<Start> start_event_;
 
+  NewConsensusConfig::NoncriticalParams current_noncritical_params_;
+
   std::string db_path() const {
     return PSTRING() << params_.db_root << "/consensus/consensus." << params_.shard.workchain << "."
                      << params_.shard.shard << "." << params_.validator_set->get_catchain_seqno() << "."
```

### validator/consensus/bus.cpp
```diff
@@ -132,4 +132,14 @@ std::string TraceEvent::contents_to_string() const {
   return PSTRING() << "{event=" << event->to_string() << "}";
 }
 
+std::string NoncriticalParamsUpdated::contents_to_string() const {
+  td::StringBuilder sb;
+#define APPEND_PARAM(_, name, value) sb << #name << "=" << params.name << ", ";
+#define APPEND_DURATION(_, name, value) sb << #name << "=" << params.name.count() << "ms, ";
+  ENUMERATE_NONCRITICAL_PARAMS(APPEND_PARAM, APPEND_PARAM, APPEND_DURATION)
+#undef APPEND_PARAM
+#undef APPEND_DURATION
+  return PSTRING() << "{params={" << td::Slice{sb.as_cslice()}.remove_suffix(2) << "}}";
+}
+
 }  // namespace ton::validator::consensus
```

### validator/consensus/bus.h
```diff
@@ -134,6 +134,12 @@ struct TraceEvent {
   std::string contents_to_string() const;
 };
 
+struct NoncriticalParamsUpdated {
+  NewConsensusConfig::NoncriticalParams params;
+
+  std::string contents_to_string() const;
+};
+
 class Db {
  public:
   virtual ~Db() = default;
@@ -148,10 +154,10 @@ class Db {
 
 class Bus : public td::actor::Bus {
  public:
-  using Events =
-      td::TypeList<Start, StopRequested, FinalizeBlock, OurLeaderWindowStarted, CandidateGenerated, CandidateReceived,
-                   ValidationRequest, IncomingProtocolMessage, OutgoingProtocolMessage, IncomingOverlayRequest,
-                   OutgoingOverlayRequest, BlockFinalizedInMasterchain, MisbehaviorReport, TraceEvent>;
+  using Events = td::TypeList<Start, StopRequested, FinalizeBlock, OurLeaderWindowStarted, CandidateGenerated,
+                              CandidateReceived, ValidationRequest, IncomingProtocolMessage, OutgoingProtocolMessage,
+                              IncomingOverlayRequest, OutgoingOverlayRequest, BlockFinalizedInMasterchain,
+                              MisbehaviorReport, TraceEvent, NoncriticalParamsUpdated>;
 
   Bus() = default;
   ~Bus() override {
```

### validator/consensus/simplex/bus.cpp
```diff
@@ -86,7 +86,7 @@ class SimplexCollatorSchedule : public CollatorSchedule {
 
 void Bus::populate_collator_schedule() {
   auto validators = static_cast<td::uint32>(validator_set.size());
-  collator_schedule = td::make_ref<SimplexCollatorSchedule>(simplex_config.slots_per_leader_window, validators);
+  collator_schedule = td::make_ref<SimplexCollatorSchedule>(config.slots_per_leader_window, validators);
 }
 
 }  // namespace ton::validator::consensus::simplex
```

### validator/consensus/simplex/bus.h
```diff
@@ -103,22 +103,10 @@ class Bus : public consensus::Bus {
 
   void populate_collator_schedule() override;
 
-  NewConsensusConfig::Simplex simplex_config;
-
   std::vector<CertificateRef<Vote>> bootstrap_certificates;
   std::vector<Vote> bootstrap_votes;
 
   td::uint32 first_nonannounced_window = 0;
-
-  // FIXME: These should come from validator options
-  double first_block_timeout_multipler = 1.05;
-  double first_block_max_timeout_s = 100;
-  double standstill_timeout_s = 10;
-
-  // Candidate resolution timeout settings
-  double candidate_resolve_initial_timeout_s = 0.5;
-  double candidate_resolve_timeout_multiplier = 1.5;
-  double candidate_resolve_max_timeout_s = 30.0;
 };
 
 using BusHandle = td::actor::BusHandle<Bus>;
```

### validator/consensus/simplex/candidate-resolver.cpp
```diff
@@ -108,6 +108,7 @@ class CandidateResolverImpl : public td::actor::SpawnsWith<Bus>, public td::acto
   TON_RUNTIME_DEFINE_EVENT_HANDLER();
 
   void start_up() override {
+    params_ = owning_bus()->config.noncritical_params;
     load_from_db();
   }
 
@@ -127,6 +128,11 @@ class CandidateResolverImpl : public td::actor::SpawnsWith<Bus>, public td::acto
     stop();
   }
 
+  template <>
+  void handle(BusHandle, std::shared_ptr<const NoncriticalParamsUpdated> event) {
+    params_ = event->params;
+  }
+
   template <>
   td::actor::Task<ProtocolMessage> process(BusHandle, std::shared_ptr<IncomingOverlayRequest> event) {
     auto request = co_await fetch_tl_object<tl::requestCandidate>(event->request.data, true);
@@ -205,6 +211,7 @@ class CandidateResolverImpl : public td::actor::SpawnsWith<Bus>, public td::acto
     std::vector<td::Promise<td::Unit>> store_awaiters;
   };
 
+  NewConsensusConfig::NoncriticalParams params_;
   std::map<CandidateId, CandidateState> state_;
 
   void load_from_db() {
@@ -291,7 +298,7 @@ class CandidateResolverImpl : public td::actor::SpawnsWith<Bus>, public td::acto
       co_return {};
     }
 
-    double timeout_s = bus.candidate_resolve_initial_timeout_s;
+    std::chrono::duration<double> timeout = params_.candidate_resolve_timeout;
 
     while (!state.candidate_and_cert.is_complete()) {
       auto request_tl = state.candidate_and_cert.make_request(id);
@@ -303,9 +310,9 @@ class CandidateResolverImpl : public td::actor::SpawnsWith<Bus>, public td::acto
       }
       PeerValidatorId peer{peer_idx};
 
-      auto timeout = td::Timestamp::in(timeout_s);
-      auto maybe_response =
-          co_await owning_bus().publish<OutgoingOverlayRequest>(peer, timeout, std::move(request)).wrap();
+      auto maybe_response = co_await owning_bus()
+                                .publish<OutgoingOverlayRequest>(peer, td::Timestamp::in(timeout), std::move(request))
+                                .wrap();
 
       if (maybe_response.is_ok()) {
         auto response = maybe_response.move_as_ok();
@@ -318,7 +325,8 @@ class CandidateResolverImpl : public td::actor::SpawnsWith<Bus>, public td::acto
         }
       }
 
-      timeout_s = std::min(timeout_s * bus.candidate_resolve_timeout_multiplier, bus.candidate_resolve_max_timeout_s);
+      timeout = std::min<std::chrono::duration<double>>(timeout * params_.candidate_resolve_timeout_multiplier,
+                                                        params_.candidate_resolve_timeout_cap);
     }
 
     co_return {};
```

### validator/consensus/simplex/consensus.cpp
```diff
@@ -37,11 +37,9 @@ class ConsensusImpl : public td::actor::SpawnsWith<Bus>, public td::actor::Conne
 
     auto& bus = *owning_bus();
 
-    slots_per_leader_window_ = bus.simplex_config.slots_per_leader_window;
-    max_leader_window_desync_ = bus.simplex_config.max_leader_window_desync;
-    target_rate_s_ = bus.config.target_rate_ms / 1000.;
-    default_first_block_timeout_s_ = bus.simplex_config.first_block_timeout_ms / 1000.;
-    first_block_timeout_s_ = default_first_block_timeout_s_;
+    slots_per_leader_window_ = bus.config.slots_per_leader_window;
+    params_ = bus.config.noncritical_params;
+    first_block_timeout_ = params_.first_block_timeout;
     state_.emplace(State({}));
 
     for (const auto& vote : bus.bootstrap_votes) {
@@ -97,6 +95,11 @@ class ConsensusImpl : public td::actor::SpawnsWith<Bus>, public td::actor::Conne
     stop();
   }
 
+  template <>
+  void handle(BusHandle, std::shared_ptr<const NoncriticalParamsUpdated> event) {
+    params_ = event->params;
+  }
+
   template <>
   void handle(BusHandle, std::shared_ptr<const FinalizationObserved> event) {
     state_->notify_finalized(event->id.slot);
@@ -114,10 +117,10 @@ class ConsensusImpl : public td::actor::SpawnsWith<Bus>, public td::actor::Conne
     current_window_ = new_window;
 
     if (previous_window_had_skip_) {
-      first_block_timeout_s_ =
-          std::min(first_block_timeout_s_ * bus.first_block_timeout_multipler, bus.first_block_max_timeout_s);
+      first_block_timeout_ = std::min<std::chrono::duration<double>>(
+          first_block_timeout_ * params_.first_block_timeout_multiplier, params_.first_block_timeout_cap);
     } else {
-      first_block_timeout_s_ = default_first_block_timeout_s_;
+      first_block_timeout_ = params_.first_block_timeout;
     }
 
     td::uint32 offset = event->start_slot % slots_per_leader_window_;
@@ -131,8 +134,8 @@ class ConsensusImpl : public td::actor::SpawnsWith<Bus>, public td::actor::Conne
 
     if (timeout_slot_ <= event->start_slot) {
       timeout_slot_ = event->start_slot + 1;
-      timeout_base_ = td::Timestamp::in(first_block_timeout_s_);
-      alarm_timestamp() = td::Timestamp::in(target_rate_s_, timeout_base_);
+      timeout_base_ = td::Timestamp::in(first_block_timeout_);
+      alarm_timestamp() = td::Timestamp::in(params_.target_rate, timeout_base_);
     }
   }
 
@@ -154,7 +157,7 @@ class ConsensusImpl : public td::actor::SpawnsWith<Bus>, public td::actor::Conne
   template <>
   void handle(BusHandle, std::shared_ptr<const CandidateReceived> event) {
     td::uint32 slot_idx = event->candidate->id.slot;
-    td::uint32 first_too_new_slot = (current_window_ + max_leader_window_desync_ + 1) * slots_per_leader_window_;
+    td::uint32 first_too_new_slot = (current_window_ + params_.max_leader_window_desync + 1) * slots_per_leader_window_;
     if (slot_idx >= first_too_new_slot) {
       LOG(WARNING) << "Dropping too new candidate from " << event->candidate->leader << " : slot=" << slot_idx
                    << ", current_window=" << current_window_ * slots_per_leader_window_;
@@ -194,8 +197,8 @@ class ConsensusImpl : public td::actor::SpawnsWith<Bus>, public td::actor::Conne
     auto parent = co_await owning_bus().publish<ResolveState>(base);
     td::Timestamp start_time = td::Timestamp::now();
     if (parent.gen_utime_exact.has_value()) {
-      start_time = std::max(start_time, td::Timestamp::at_unix(*parent.gen_utime_exact + target_rate_s_));
-      start_time = std::min(start_time, td::Timestamp::in(target_rate_s_));
+      start_time = std::max(start_time, td::Timestamp::at_unix(*parent.gen_utime_exact) + params_.target_rate);
+      start_time = std::min(start_time, td::Timestamp::in(params_.target_rate));
     }
 
     if (current_window_ != start_slot / slots_per_leader_window_) {
@@ -257,7 +260,7 @@ class ConsensusImpl : public td::actor::SpawnsWith<Bus>, public td::actor::Conne
       // NotarCert of the previous slot but in case we missed the certificate let's give the
       // certificate as much time as protocol allows to arrive.
       alarm_timestamp() = td::Timestamp::in(
-          (timeout_slot_ - current_window_ * slots_per_leader_window_) * target_rate_s_, timeout_base_);
+          (timeout_slot_ - current_window_ * slots_per_leader_window_) * params_.target_rate, timeout_base_);
     }
 
     slot->state->notar_cert = event->id;
@@ -275,12 +278,11 @@ class ConsensusImpl : public td::actor::SpawnsWith<Bus>, public td::actor::Conne
   }
 
   td::uint32 slots_per_leader_window_;
-  td::uint32 max_leader_window_desync_;
+  NewConsensusConfig::NoncriticalParams params_;
+
   td::Timestamp timeout_base_;
   td::uint32 timeout_slot_ = 0;  // By alarm_timestamp(), slots < timeout_slot_ should be notarized.
-  double target_rate_s_;
-  double default_first_block_timeout_s_;
-  double first_block_timeout_s_;
+  std::chrono::duration<double> first_block_timeout_;
   bool previous_window_had_skip_ = false;
   std::optional<State> state_;
   td::uint32 current_window_ = 0;
```
