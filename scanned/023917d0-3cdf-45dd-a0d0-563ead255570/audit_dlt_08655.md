# [?] fixed crash in validator. Updated elector/config smartcontracts

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2020-04-02
Source: https://github.com/ton-blockchain/ton/commit/0e4277313c5e6f756a2e7fb8123d8b7091fba349
Type: security-commit

## Details
fixed crash in validator. Updated elector/config smartcontracts

## Patch
### crypto/block/block.cpp
```diff
@@ -578,6 +578,15 @@ bool MsgProcessedUptoCollection::already_processed(const EnqueuedMsgDescr& msg)
   return false;
 }
 
+bool MsgProcessedUptoCollection::can_check_processed() const {
+  for (const auto& entry : list) {
+    if (!entry.can_check_processed()) {
+      return false;
+    }
+  }
+  return true;
+}
+
 bool MsgProcessedUptoCollection::for_each_mcseqno(std::function<bool(ton::BlockSeqno)> func) const {
   for (const auto& entry : list) {
     if (!func(entry.mc_seqno)) {
```

### crypto/block/block.h
```diff
@@ -171,6 +171,9 @@ struct MsgProcessedUpto {
                 ton::BlockSeqno other_mc_seqno) const &;
   // NB: this is for checking whether we have already imported an internal message
   bool already_processed(const EnqueuedMsgDescr& msg) const;
+  bool can_check_processed() const {
+    return (bool)compute_shard_end_lt;
+  }
 };
 
 struct MsgProcessedUptoCollection {
@@ -197,6 +200,7 @@ struct MsgProcessedUptoCollection {
   bool combine_with(const MsgProcessedUptoCollection& other);
   // NB: this is for checking whether we have already imported an internal message
   bool already_processed(const EnqueuedMsgDescr& msg) const;
+  bool can_check_processed() const;
   bool for_each_mcseqno(std::function<bool(ton::BlockSeqno)>) const;
 };
 
```

### crypto/block/block.tlb
```diff
@@ -603,6 +603,9 @@ workchain#a6 enabled_since:uint32 actual_min_split:(## 8)
 
 _ workchains:(HashmapE 32 WorkchainDescr) = ConfigParam 12;
 
+complaint_prices#1a deposit:Grams bit_price:Grams cell_price:Grams = ComplaintPricing; 
+_ ComplaintPricing = ConfigParam 13;
+
 block_grams_created#6b masterchain_block_fee:Grams basechain_block_fee:Grams
   = BlockCreateFees;
 _ BlockCreateFees = ConfigParam 14;
@@ -696,6 +699,13 @@ top_block_descr#d5 proof_for:BlockIdExt signatures:(Maybe ^BlockSignatures)
 //
 top_block_descr_set#4ac789f3 collection:(HashmapE 96 ^TopBlockDescr) = TopBlockDescrSet;
 
+//
+//  VALIDATOR MISBEHAVIOR COMPLAINTS
+//
+no_blk_gen mc_blk_ref:ExtBlkRef from_utime:uint32 to_utime:uint32 state_proof:^Cell prod_proof:^Cell = ComplaintDescr;
+validator_complaint#ba validator_pubkey:uint256 description:^ComplaintDescr severity:uint8 reward_addr:uint256 paid:Grams suggested_fine:Grams suggested_fine_part:uint32 = ValidatorComplaint;
+complaint_status#2d complaint:^ValidatorComplaint voters:(HashmapE 16 True) vset_id:uint256 weight_remaining:int64 = ValidatorComplaintStatus;
+
 //
 //  TVM REFLECTION
 //
```

### crypto/smartcont/CreateState.fif
```diff
@@ -109,6 +109,10 @@ variable special-dict
 { swap cfg-prop-setup swap cfg-prop-setup <b x{91} s, rot ref, swap ref, b> } : make-proposals-setup
 { make-proposals-setup 11 config! } : config.param_proposals_setup!
 
+// deposit bit_pps cell_pps
+{ 3 0 reverse <b x{1a} s, swap Gram, swap Gram, swap Gram, b> } : create-complaint-pricing
+{ create-complaint-pricing 13 config! } : config.complaint_prices!
+
 // bit-pps cell-pps mc-bit-pps mc-cell-pps --
 { <b x{cc} s, 0 32 u, 4 roll 64 u, 3 roll 64 u, rot 64 u, swap 64 u,
   0 dictnew 32 b>udict! 0= abort"cannot create storage prices dictionary"
```

### crypto/smartcont/config-code.fc
```diff
@@ -397,7 +397,7 @@ int register_voting_proposal(slice cs, int msg_value) impure inline_ref {
       hash = -0xcd506e6c;  ;; cannot set mandatory parameter to null
     }
   }
-  if (param_val.cell_depth() >= 256) {
+  if (param_val.cell_depth() >= 128) {
     hash = -0xc2616456;  ;; bad value
   }
   if (hash < -1) {
```

### crypto/smartcont/elector-code.fc
```diff
@@ -1,34 +1,34 @@
 ;; Elector smartcontract
 
-;; cur_elect credits past_elect grams active_id active_hash
-(cell, cell, cell, int, int, int) load_data() {
+;; cur_elect credits past_elections grams active_id active_hash
+(cell, cell, cell, int, int, int) load_data() inline_ref {
   var cs = get_data().begin_parse();
   var res = (cs~load_dict(), cs~load_dict(), cs~load_dict(), cs~load_grams(), cs~load_uint(32), cs~load_uint(256));
   cs.end_parse();
   return res;
 }
 
-;; cur_elect credits past_elect grams active_id active_hash
-() store_data(elect, credits, past_elect, grams, active_id, active_hash) impure {
+;; cur_elect credits past_elections grams active_id active_hash
+() store_data(elect, credits, past_elections, grams, active_id, active_hash) impure inline_ref {
   set_data(begin_cell()
     .store_dict(elect)
     .store_dict(credits)
-    .store_dict(past_elect)
+    .store_dict(past_elections)
     .store_grams(grams)
     .store_uint(active_id, 32)
     .store_uint(active_hash, 256)
   .end_cell());
 }
 
 ;; elect -> elect_at elect_close min_stake total_stake members failed finished
-_ unpack_elect(elect) {
+_ unpack_elect(elect) inline_ref {
   var es = elect.begin_parse();
   var res = (es~load_uint(32), es~load_uint(32), es~load_grams(), es~load_grams(), es~load_dict(), es~load_int(1), es~load_int(1));
   es.end_parse();
   return res;
 }
 
-cell pack_elect(elect_at, elect_close, min_stake, total_stake, members, failed, finished) {
+cell pack_elect(elect_at, elect_close, min_stake, total_stake, members, failed, finished) inline_ref {
   return begin_cell()
     .store_uint(elect_at, 32)
     .store_uint(elect_close, 32)
@@ -40,13 +40,86 @@ cell pack_elect(elect_at, elect_close, min_stake, total_stake, members, failed,
   .end_cell();
 }
 
+;; slice -> unfreeze_at stake_held vset_hash frozen_dict total_stake bonuses complaints
+_ unpack_past_election(slice fs) inline_ref {
+  var res = (fs~load_uint(32), fs~load_uint(32), fs~load_uint(256), fs~load_dict(), fs~load_grams(), fs~load_grams(), fs~load_dict());
+  fs.end_parse();
+  return res;
+}
+
+builder pack_past_election(int unfreeze_at, int stake_held, int vset_hash, cell frozen_dict, int total_stake, int bonuses, cell complaints) inline_ref {
+  return begin_cell()
+      .store_uint(unfreeze_at, 32)
+      .store_uint(stake_held, 32)
+      .store_uint(vset_hash, 256)
+      .store_dict(frozen_dict)
+      .store_grams(total_stake)
+      .store_grams(bonuses)
+      .store_dict(complaints);
+}
+
+;; complaint_status#2d complaint:^ValidatorComplaint voters:(HashmapE 16 True)
+;;   vset_id:uint256 weight_remaining:int64 = ValidatorComplaintStatus;
+_ unpack_complaint_status(slice cs) inline_ref {
+  throw_unless(9, cs~load_uint(8) == 0x2d);
+  var res = (cs~load_ref(), cs~load_dict(), cs~load_uint(256), cs~load_int(64));
+  cs.end_parse();
+  return res;
+}
+
+builder pack_complaint_status(cell complaint, cell voters, int vset_id, int weight_remaining) inline_ref {
+  return begin_cell()
+    .store_uint(0x2d, 8)
+    .store_ref(complaint)
+    .store_dict(voters)
+    .store_uint(vset_id, 256)
+    .store_int(weight_remaining, 64);
+}
+
+;; validator_complaint#ba validator_pubkey:uint256 description:^ComplaintDescr
+;;   severity:uint8 reward_addr:uint256 paid:Grams suggested_fine:Grams
+;;   suggested_fine_part:uint32 = ValidatorComplaint;
+_ unpack_complaint(slice cs) inline_ref {
+  throw_unless(9, cs~load_int(8) == 0xba - 0x100);
+  var res = (cs~load_uint(256), cs~load_ref(), cs~load_uint(8), cs~load_uint(256), cs~load_grams(), cs~load_grams(), cs~load_uint(32));
+  cs.end_parse();
+  return res;
+}
+
+builder pack_complaint(int validator_pubkey, cell description, int severity, int reward_addr, int paid, int suggested_fine, int suggested_fine_part) inline_ref {
+  return begin_cell()
+    .store_int(0xba - 0x100, 8)
+    .store_uint(validator_pubkey, 256)
+    .store_ref(description)
+    .store_uint(severity, 8)
+    .store_uint(reward_addr, 256)
+    .store_grams(paid)
+    .store_grams(suggested_fine)
+    .store_uint(suggested_fine_part, 32);
+}
+
+;; complaint_prices#1a deposit:Grams bit_price:Grams cell_price:Grams = ComplaintPricing; 
+(int, int, int) parse_complaint_prices(cell info) inline {
+  var cs = info.begin_parse();
+  throw_unless(9, cs~load_uint(8) == 0x1a);
+  var res = (cs~load_grams(), cs~load_grams(), cs~load_grams());
+  cs.end_parse();
+  return res;
+}
+
+;; deposit bit_price cell_price
+(int, int, int) get_complaint_prices() inline_ref {
+  var info = config_param(13);
+  return info.null?() ? (1 << 36, 1, 512) : info.parse_complaint_prices();
+}
+
 ;; elected_for elections_begin_before elections_end_before stake_held_for
 (int, int, int, int) get_validator_conf() {
   var cs = config_param(15).begin_parse();
   return (cs~load_int(32), cs~load_int(32), cs~load_int(32), cs.preload_int(32));
 }
 
-() send_message_back(addr, ans_tag, query_id, body, grams, mode) impure {
+() send_message_back(addr, ans_tag, query_id, body, grams, mode) impure inline_ref {
   ;; int_msg_info$0 ihr_disabled:Bool bounce:Bool bounced:Bool src:MsgAddress -> 011000
   var msg = begin_cell()
     .store_uint(0x18, 6)
@@ -61,15 +134,15 @@ cell pack_elect(elect_at, elect_close, min_stake, total_stake, members, failed,
   send_raw_message(msg.end_cell(), mode);
 }
 
-() return_stake(addr, query_id, reason) impure {
+() return_stake(addr, query_id, reason) impure inline_ref {
   return send_message_back(addr, 0xee6f454c, query_id, reason, 0, 64);
 }
 
-() send_confirmation(addr, query_id, comment) impure {
+() send_confirmation(addr, query_id, comment) impure inline_ref {
   return send_message_back(addr, 0xf374484c, query_id, comment, 1000000000, 2);
 }
 
-() send_validator_set_to_config(config_addr, vset, query_id) impure {
+() send_validator_set_to_config(config_addr, vset, query_id) impure inline_ref {
   var msg = begin_cell()
     .store_uint(0xc4ff, 17)   ;; 0 11000100 0xff 
     .store_uint(config_addr, 256)
@@ -82,7 +155,7 @@ cell pack_elect(elect_at, elect_close, min_stake, total_stake, members, failed,
 }
 
 ;; credits 'amount' to 'addr' inside credit dictionary 'credits'
-_ ~credit_to(credits, addr, amount) {
+_ ~credit_to(credits, addr, amount) inline_ref {
   var (val, f) = credits.udict_get?(256, addr);
   if (f) {
     amount += val~load_grams();
@@ -91,11 +164,11 @@ _ ~credit_to(credits, addr, amount) {
   return (credits, ());
 }
 
-() process_new_stake(s_addr, msg_value, cs, query_id) impure {
+() process_new_stake(s_addr, msg_value, cs, query_id) impure inline_ref {
   var (src_wc, src_addr) = parse_std_addr(s_addr);
   var ds = get_data().begin_parse();
   var elect = ds~load_dict();
-  if (null?(elect) | (src_wc + 1)) {
+  if (elect.null?() | (src_wc + 1)) {
     ;; no elections active, or source is not in masterchain
     ;; bounce message
     return return_stake(s_addr, query_id, 0);
@@ -172,7 +245,7 @@ _ ~credit_to(credits, addr, amount) {
   return ();
 }
 
-(cell, int) unfreeze_without_bonuses(credits, freeze_dict, tot_stakes) {
+(cell, int) unfreeze_without_bonuses(credits, freeze_dict, tot_stakes) inline_ref {
   var total = var recovered = 0;
   var pubkey = -1;
   do {
@@ -192,7 +265,7 @@ _ ~credit_to(credits, addr, amount) {
   return (credits, recovered);
 }
 
-(cell, int) unfreeze_with_bonuses(credits, freeze_dict, tot_stakes, tot_bonuses) {
+(cell, int) unfreeze_with_bonuses(credits, freeze_dict, tot_stakes, tot_bonuses) inline_ref {
   var total = var recovered = var returned_bonuses = 0;
   var pubkey = -1;
   do {
@@ -214,21 +287,20 @@ _ ~credit_to(credits, addr, amount) {
   return (credits, recovered + tot_bonuses - returned_bonuses);
 }
 
-_ unfreeze_all(credits, past_elections, elect_id) {
+_ unfreeze_all(credits, past_elections, elect_id) inline_ref {
   var (fs, f) = past_elections~udict_delete_get?(32, elect_id);
   ifnot (f) {
     ;; no elections with this id
     return (credits, past_elections, 0);
   }
-  var (data1, vset_hash, fdict, tot_stakes, bonuses, complaints) = (fs~load_uint(64), fs~load_uint(256), fs~load_dict(), fs~load_grams(), fs~load_grams(), fs~load_dict());
-  fs.end_parse();
+  var (unfreeze_at, stake_held, vset_hash, fdict, tot_stakes, bonuses, complaints) = fs.unpack_past_election();
   var unused_prizes = (bonuses > 0) ?
     credits~unfreeze_with_bonuses(fdict, tot_stakes, bonuses) :
     credits~unfreeze_without_bonuses(fdict, tot_stakes);
   return (credits, past_elections, unused_prizes);
 }
 
-() config_set_confirmed(s_addr, cs, query_id, ok) impure {
+() config_set_confirmed(s_addr, cs, query_id, ok) impure inline_ref {
   var (src_wc, src_addr) = parse_std_addr(s_addr);
   var config_addr = config_param(0).begin_parse().preload_uint(256);
   var ds = get_data().begin_parse();
@@ -259,37 +331,31 @@ _ unfreeze_all(credits, past_elections, elect_id) {
   ;; ... do not remove elect until we see this set as the next elected validator set
 }
 
-() process_simple_transfer(s_addr, msg_value) impure {
-  var (elect, credits, past_elect, grams, active_id, active_hash) = load_data();
+() process_simple_transfer(s_addr, msg_value) impure inline_ref {
+  var (elect, credits, past_elections, grams, active_id, active_hash) = load_data();
   (int src_wc, int src_addr) = parse_std_addr(s_addr);
   if (src_addr | (src_wc + 1) | (active_id == 0)) {
     ;; simple transfer to us (credit "nobody's" account)
     ;; (or no known active validator set)
     grams += msg_value;
-    return store_data(elect, credits, past_elect, grams, active_id, active_hash);
+    return store_data(elect, credits, past_elections, grams, active_id, active_hash);
   }
   ;; zero source address -1:00..00 (collecting validator fees)
-  var (fs, f) = past_elect.udict_get?(32, active_id);
+  var (fs, f) = past_elections.udict_get?(32, active_id);
   ifnot (f) {
     ;; active validator set not found (?)
     grams += msg_value;
   } else {
     ;; credit active validator set bonuses
-    var (data, hash, dict, total_stake, bonuses) = (fs~load_uint(64), fs~load_uint(256), fs~load_dict(), fs~load_grams(), fs~load_grams());
+    var (unfreeze_at, stake_held, hash, dict, total_stake, bonuses, complaints) = fs.unpack_past_election();
     bonuses += msg_value;
-    past_elect~udict_set_builder(32, active_id, begin_cell()
-      .store_uint(data, 64)
-      .store_uint(hash, 256)
-      .store_dict(dict)
-      .store_grams(total_stake)
-      .store_grams(bonuses)
-      .store_slice(fs));
+    past_elections~udict_set_builder(32, active_id,
+      pack_past_election(unfreeze_at, stake_held, hash, dict, total_stake, bonuses, complaints));
   }
-  store_data(elect, credits, past_elect, grams, active_id, active_hash);
-  return ();
+  return store_data(elect, credits, past_elections, grams, active_id, active_hash);
 }
 
-() recover_stake(op, s_addr, cs, query_id) impure {
+() recover_stake(op, s_addr, cs, query_id) impure inline_ref {
   (int src_wc, int src_addr) = parse_std_addr(s_addr);
   if (src_wc + 1) {
     ;; not from masterchain, return error
@@ -322,7 +388,7 @@ _ unfreeze_all(credits, past_elections, elect_id) {
   return send_message_back(s_addr, 0xce436f64, query_id, op, 0, 64);
 }
 
-int upgrade_code(s_addr, cs, query_id) {
+int upgrade_code(s_addr, cs, query_id) inline_ref {
   var c_addr = config_param(0);
   if (c_addr.null?()) {
     ;; no configuration smart contract known
@@ -339,13 +405,71 @@ int upgrade_code(s_addr, cs, query_id) {
   set_code(code);
   ifnot(cs.slice_empty?()) {
     set_c3(code.begin_parse().bless());
-    ;; run_method3(1666, s_addr, cs, query_id);
     after_code_upgrade(s_addr, cs, query_id);
     throw(0);
   }
   return true;
 }
 
+int register_complaint(s_addr, complaint, msg_value) {
+  var (src_wc, src_addr) = parse_std_addr(s_addr);
+  if (src_wc + 1) { ;; not from masterchain, return error
+    return -1;
+  }
+  if (complaint.slice_depth() >= 128) {
+    return -3;  ;; invalid complaint
+  }
+  var (elect, credits, past_elections, grams, active_id, active_hash) = load_data();
+  var election_id = complaint~load_uint(32);
+  var (fs, f) = past_elections.udict_get?(32, election_id);
+  ifnot (f) {  ;; election not found
+    return -2;
+  }
+  var expire_in = fs.preload_uint(32) - now();
+  if (expire_in <= 0) { ;; already expired
+    return -4;
+  }
+  var (validator_pubkey, description, severity, reward_addr, paid, suggested_fine, suggested_fine_part) = unpack_complaint(complaint);
+  reward_addr = src_addr;
+  ;; compute complaint storage/creation price
+  var (deposit, bit_price, cell_price) = get_complaint_prices();
+  var (_, bits, refs) = slice_compute_data_size(complaint, 4096);
+  var pps = (bits + 1024) * bit_price + (refs + 2) * cell_price;
+  paid = pps * expire_in + deposit;
+  if (paid + (1 << 30) < msg_value) { ;; not enough money
+    return -5;
+  }
+  ;; re-pack modified complaint
+  cell complaint = pack_complaint(validator_pubkey, description, severity, reward_addr, paid, suggested_fine, suggested_fine_part).end_cell();
+  var (unfreeze_at, stake_held, vset_hash, frozen_dict, total_stake, bonuses, complaints) = unpack_past_election(fs);
+  var (fs, f) = frozen_dict.udict_get?(256, validator_pubkey);
+  ifnot (f) { ;; no such validator, cannot complain
+    return -6;
+  }
+  var validator_stake = fs~load_grams();
+  int fine = suggested_fine + muldiv(validator_stake, suggested_fine_part, 1 << 32);
+  if (fine > validator_stake) {  ;; validator's stake is less than suggested fine
+    return -7;
+  }
+  if (fine <= paid) {  ;; fine is less than the money paid for creating complaint
+    return -8;
+  }
+  ;; create complaint status
+  var cstatus = pack_complaint_status(complaint, null(), 0, 0);
+  ;; save complaint status into complaints
+  var cpl_id = complaint.cell_hash();
+  ifnot (complaints~udict_add_builder?(256, cpl_id, cstatus)) {
+    return -9;   ;; complaint already exists
+  }
+  ;; pack past election info
+  past_elections~udict_set_builder(32, election_id, pack_past_election(unfreeze_at, stake_held, vset_hash, frozen_dict, total_stake, bonuses, complaints));
+  ;; pack persistent data
+  ;; next line can be commented, but it saves a lot of stack manipulations
+  var (elect, credits, _, grams, active_id, active_hash) = load_data();
+  store_data(elect, credits, past_elections, grams, active_id, active_hash);
+  return 0;
+}
+
 () recv_internal(int msg_value, cell in_msg_cell, slice in_msg) impure {
   ;; do nothing for internal messages
   var cs = in_msg_cell.begin_parse();
@@ -383,6 +507,19 @@ int upgrade_code(s_addr, cs, query_id) {
     ;; confirmation from configuration smart contract
     return config_set_confirmed(s_addr, in_msg, query_id, cfg_ok);
   }
+  if (op == 0x52674370) {
+    ;; new complaint 
+    var price = register_complaint(s_addr, in_msg, msg_value);
+    int mode = 64;
+    int ans_tag = - price;
+    if (price >= 0) {
+      ;; ok, debit price
+      raw_reserve(price, 4);
+      ans_tag = 0;
+      mode = 128;
+    }
+    return send_message_back(s_addr, ans_tag + 0xf2676350, query_id, op, 0, mode);
+  }
   ifnot (op & (1 << 31)) {
     ;; unknown query, return error
     return send_message_back(s_addr, 0xffffffff, query_id, op, 0, 64);
@@ -396,7 +533,7 @@ int postpone_elections() impure {
 }
 
 ;; computes the total stake out of the first n entries of list l
-_ compute_total_stake(l, n, m_stake) {
+_ compute_total_stake(l, n, m_stake) inline_ref {
   int tot_stake = 0;
   repeat (n) {
     (var h, l) = uncons(l);
@@ -574,51 +711,46 @@ int conduct_elections(ds, elect, credits) impure {
   var config_addr = config_param(0).begin_parse().preload_uint(256);
   send_validator_set_to_config(config_addr, vset, elect_at);
   ;; add frozen to the dictionary of past elections
-  var past_elect = ds~load_dict();
-  past_elect~udict_set_builder(32, elect_at, begin_cell()
-    .store_uint(start + elect_for + stake_held, 32)
-    .store_uint(stake_held, 32)
-    .store_uint(cell_hash(vset), 256)
-    .store_dict(frozen)
-    .store_grams(total_stakes)
-    .store_grams(0)
-    .store_int(false, 1));
+  var past_elections = ds~load_dict();
+  past_elections~udict_set_builder(32, elect_at, pack_past_election(
+    start + elect_for + stake_held, stake_held, vset.cell_hash(),
+    frozen, total_stakes, 0, null()));
   ;; store credits and frozen until end
   set_data(begin_cell()
     .store_dict(elect)
     .store_dict(credits)
-    .store_dict(past_elect)
+    .store_dict(past_elections)
     .store_slice(ds)
   .end_cell());
   return true;
 }
 
 int update_active_vset_id() impure {
-  var (elect, credits, past_elect, grams, active_id, active_hash) = load_data();
+  var (elect, credits, past_elections, grams, active_id, active_hash) = load_data();
   var cur_hash = config_param(34).cell_hash();
   if (cur_hash == active_hash) {
     ;; validator set unchanged
     return false;
   }
   if (active_id) {
     ;; active_id becomes inactive
-    var (fs, f) = past_elect.udict_get?(32, active_id);
+    var (fs, f) = past_elections.udict_get?(32, active_id);
     if (f) {
       ;; adjust unfreeze time of this validator set
       var unfreeze_time = fs~load_uint(32);
       var fs0 = fs;
       var (stake_held, hash) = (fs~load_uint(32), fs~load_uint(256));
       throw_unless(57, hash == active_hash);
       unfreeze_time = now() + stake_held;
-      past_elect~udict_set_builder(32, active_id, begin_cell()
+      past_elections~udict_set_builder(32, active_id, begin_cell()
         .store_uint(unfreeze_time, 32)
         .store_slice(fs0));
     }
   }
   ;; look up new active_id by hash
   var id = -1;
   do {
-    (id, var fs, var f) = past_elect.udict_get_next?(32, id);
+    (id, var fs, var f) = past_elections.udict_get_next?(32, id);
     if (f) {
       var (tm, hash) = (fs~load_uint(64), fs~load_uint(256));
       if (hash == cur_hash) {
@@ -629,7 +761,7 @@ int update_active_vset_id() impure {
         grams -= amount;
         bonuses += amount;
         ;; serialize back
-        past_elect~udict_set_builder(32, id, begin_cell()
+        past_elections~udict_set_builder(32, id, begin_cell()
           .store_uint(tm, 64)
           .store_uint(hash, 256)
           .store_dict(dict)
@@ -643,11 +775,11 @@ int update_active_vset_id() impure {
   } until (~ f);
   active_id = (id.null?() ? 0 : id);
   active_hash = cur_hash;
-  store_data(elect, credits, past_elect, grams, active_id, active_hash);
+  store_data(elect, credits, past_elections, grams, active_id, active_hash);
   return true;
 }
 
-int cell_hash_eq?(cell vset, int expected_vset_hash) {
+int cell_hash_eq?(cell vset, int expected_vset_hash) inline_ref {
   return vset.null?() ? false : cell_hash(vset) == expected_vset_hash;
 }
 
@@ -680,18 +812,18 @@ int validator_set_installed(ds, elect, credits) impure {
 }
 
 int check_unfreeze() impure {
-  var (elect, credits, past_elect, grams, active_id, active_hash) = load_data();
+  var (elect, credits, past_elections, grams, active_id, active_hash) = load_data();
   int id = -1;
   do {
-    (id, var fs, var f) = past_elect.udict_get_next?(32, id);
+    (id, var fs, var f) = past_elections.udict_get_next?(32, id);
     if (f) {
       var unfreeze_at = fs~load_uint(32);
       if ((unfreeze_at <= now()) & (id != active_id)) {
         ;; unfreeze!
-        (credits, past_elect, var unused_prizes) = unfreeze_all(credits, past_elect, id);
+        (credits, past_elections, var unused_prizes) = unfreeze_all(credits, past_elections, id);
         grams += unused_prizes;
         ;; unfreeze only one at time, exit loop
-        store_data(elect, credits, past_elect, grams, active_id, active_hash);
+        store_data(elect, credits, past_elections, grams, active_id, active_hash);
         ;; exit loop
         f = false;
       }
```

### crypto/smartcont/gen-zerostate.fif
```diff
@@ -210,6 +210,9 @@ _( 2 3 2 2 1000000 10000000 1 500 )
 _( 4 7 4 2 5000000 20000000 2 1000 )
 config.param_proposals_setup!
 
+// deposit bit_pps cell_pps
+GR$100 1 500 config.complaint_prices!
+
 "validator-keys" +suffix +".pub" file>B
 { dup Blen } { 32 B| swap dup ."Validator public key = " Bx. cr
   17 add-validator } while drop
```

### validator/impl/collator.cpp
```diff
@@ -176,7 +176,7 @@ void Collator::start_up() {
     LOG(DEBUG) << "sending wait_block_state() query #" << i << " for " << prev_blocks[i].to_str() << " to Manager";
     ++pending;
     td::actor::send_closure_later(manager, &ValidatorManager::wait_block_state_short, prev_blocks[i], priority(),
-                                  timeout, [self = get_self(), i](td::Result<Ref<ShardState>> res) {
+                                  timeout, [ self = get_self(), i ](td::Result<Ref<ShardState>> res) {
                                     LOG(DEBUG) << "got answer to wait_block_state query #" << i;
                                     td::actor::send_closure_later(std::move(self), &Collator::after_get_shard_state, i,
                                                                   std::move(res));
@@ -187,7 +187,7 @@ void Collator::start_up() {
       LOG(DEBUG) << "sending wait_block_data() query #" << i << " for " << prev_blocks[i].to_str() << " to Manager";
       ++pending;
       td::actor::send_closure_later(manager, &ValidatorManager::wait_block_data_short, prev_blocks[i], priority(),
-                                    timeout, [self = get_self(), i](td::Result<Ref<BlockData>> res) {
+                                    timeout, [ self = get_self(), i ](td::Result<Ref<BlockData>> res) {
                                       LOG(DEBUG) << "got answer to wait_block_data query #" << i;
                                       td::actor::send_closure_later(std::move(self), &Collator::after_get_block_data, i,
                                                                     std::move(res));
@@ -197,8 +197,8 @@ void Collator::start_up() {
   // 4. load external messages
   LOG(DEBUG) << "sending get_external_messages() query to Manager";
   ++pending;
-  td::actor::send_closure_later(manager, &ValidatorManager::get_external_messages, shard,
-                                [self = get_self()](td::Result<std::vector<Ref<ExtMessage>>> res) -> void {
+  td::actor::send_closure_later(manager, &ValidatorManager::get_external_messages,
+                                shard, [self = get_self()](td::Result<std::vector<Ref<ExtMessage>>> res)->void {
                                   LOG(DEBUG) << "got answer to get_external_messages() query";
                                   td::actor::send_closure_later(std::move(self), &Collator::after_get_external_messages,
                                                                 std::move(res));
@@ -208,8 +208,8 @@ void Collator::start_up() {
     LOG(DEBUG) << "sending get_shard_blocks() query to Manager";
     ++pending;
     td::actor::send_closure_later(
-        manager, &ValidatorManager::get_shard_blocks, prev_blocks[0],
-        [self = get_self()](td::Result<std::vector<Ref<ShardTopBlockDescription>>> res) -> void {
+        manager, &ValidatorManager::get_shard_blocks,
+        prev_blocks[0], [self = get_self()](td::Result<std::vector<Ref<ShardTopBlockDescription>>> res)->void {
           LOG(DEBUG) << "got answer to get_shard_blocks() query";
           td::actor::send_closure_later(std::move(self), &Collator::after_get_shard_blocks, std::move(res));
         });
@@ -326,7 +326,7 @@ bool Collator::request_aux_mc_state(BlockSeqno seqno, Ref<MasterchainStateQ>& st
   LOG(DEBUG) << "sending auxiliary wait_block_state() query for " << blkid.to_str() << " to Manager";
   ++pending;
   td::actor::send_closure_later(manager, &ValidatorManager::wait_block_state_short, blkid, priority(), timeout,
-                                [self = get_self(), blkid](td::Result<Ref<ShardState>> res) {
+                                [ self = get_self(), blkid ](td::Result<Ref<ShardState>> res) {
                                   LOG(DEBUG) << "got answer to wait_block_state query for " << blkid.to_str();
                                   td::actor::send_closure_later(std::move(self), &Collator::after_get_aux_shard_state,
                                                                 blkid, std::move(res));
@@ -414,8 +414,8 @@ void Collator::after_get_mc_state(td::Result<std::pair<Ref<MasterchainState>, Bl
     // NB. it is needed only for creating a correct ExtBlkRef reference to it, which requires start_lt and end_lt
     LOG(DEBUG) << "sending wait_block_data() query #-1 for " << mc_block_id_.to_str() << " to Manager";
     ++pending;
-    td::actor::send_closure_later(manager, &ValidatorManager::wait_block_data_short, mc_block_id_, priority(), timeout,
-                                  [self = get_self()](td::Result<Ref<BlockData>> res) {
+    td::actor::send_closure_later(manager, &ValidatorManager::wait_block_data_short, mc_block_id_, priority(),
+                                  timeout, [self = get_self()](td::Result<Ref<BlockData>> res) {
                                     LOG(DEBUG) << "got answer to wait_block_data query #-1";
                                     td::actor::send_closure_later(std::move(self), &Collator::after_get_block_data, -1,
                                                                   std::move(res));
@@ -567,7 +567,7 @@ bool Collator::request_neighbor_msg_queues() {
     LOG(DEBUG) << "neighbor #" << i << " : " << descr.blk_.to_str();
     ++pending;
     send_closure_later(manager, &ValidatorManager::wait_block_message_queue_short, descr.blk_, priority(), timeout,
-                       [self = get_self(), i](td::Result<Ref<MessageQueue>> res) {
+                       [ self = get_self(), i ](td::Result<Ref<MessageQueue>> res) {
                          td::actor::send_closure(std::move(self), &Collator::got_neighbor_out_queue, i, std::move(res));
                        });
     ++i;
@@ -845,6 +845,7 @@ bool Collator::add_trivial_neighbor() {
           CHECK(found == 1);
           CHECK(after_split_);
           CHECK(sibling_out_msg_queue_);
+          CHECK(sibling_processed_upto_);
           neighbors_.emplace_back(*descr_ref);
           auto& nb2 = neighbors_.at(i);
           nb2.set_queue_root(sibling_out_msg_queue_->get_root_cell());
@@ -1397,6 +1398,9 @@ bool Collator::try_collate() {
   if (!fix_processed_upto(*processed_upto_)) {
     return fatal_error("Cannot adjust ProcessedUpto of our shard state");
   }
+  if (sibling_processed_upto_ && !fix_processed_upto(*sibling_processed_upto_)) {
+    return fatal_error("Cannot adjust ProcessedUpto of the shard state of our virtual sibling");
+  }
   for (auto& descr : neighbors_) {
     CHECK(descr.processed_upto);
     if (!fix_processed_upto(*descr.processed_upto)) {
@@ -1748,6 +1752,13 @@ bool Collator::out_msg_queue_cleanup() {
     block::gen::t_OutMsgQueue.print(std::cerr, *rt);
     rt->print_rec(std::cerr);
   }
+  for (const auto& nb : neighbors_) {
+    if (!nb.is_disabled() && (!nb.processed_upto || !nb.processed_upto->can_check_processed())) {
+      return fatal_error(-667, PSTRING() << "internal error: no info for checking processed messages from neighbor "
+                                         << nb.blk_.to_str());
+    }
+  }
+
   auto res = out_msg_queue_->filter([&](vm::CellSlice& cs, td::ConstBitPtr key, int n) -> int {
     assert(n == 352);
     // LOG(DEBUG) << "key is " << key.to_hex(n);
@@ -2938,24 +2949,24 @@ bool Collator::update_shard_config(const block::WorkchainSet& wc_set, const bloc
   WorkchainId wc_id{ton::workchainInvalid};
   Ref<block::WorkchainInfo> wc_info;
   ton::BlockSeqno& min_seqno = min_ref_mc_seqno_;
-  return shard_conf_->process_sibling_shard_hashes(
-      [&wc_set, &wc_id, &wc_info, &ccvc, &min_seqno, now = now_, update_cc](block::McShardHash& cur,
-                                                                            const block::McShardHash* sibling) {
-        if (!cur.is_valid()) {
-          return -2;
-        }
-        if (wc_id != cur.workchain()) {
-          wc_id = cur.workchain();
-          auto it = wc_set.find(wc_id);
-          if (it == wc_set.end()) {
-            wc_info.clear();
-          } else {
-            wc_info = it->second;
-          }
-        }
-        min_seqno = std::min(min_seqno, cur.min_ref_mc_seqno_);
-        return update_one_shard(cur, sibling, wc_info.get(), now, ccvc, update_cc);
-      });
+  return shard_conf_->process_sibling_shard_hashes([
+    &wc_set, &wc_id, &wc_info, &ccvc, &min_seqno, now = now_, update_cc
+  ](block::McShardHash & cur, const block::McShardHash* sibling) {
+    if (!cur.is_valid()) {
+      return -2;
+    }
+    if (wc_id != cur.workchain()) {
+      wc_id = cur.workchain();
+      auto it = wc_set.find(wc_id);
+      if (it == wc_set.end()) {
+        wc_info.clear();
+      } else {
+        wc_info = it->second;
+      }
+    }
+    min_seqno = std::min(min_seqno, cur.min_ref_mc_seqno_);
+    return update_one_shard(cur, sibling, wc_info.get(), now, ccvc, update_cc);
+  });
 }
 
 bool Collator::create_mc_state_extra() {
@@ -3801,7 +3812,7 @@ bool Collator::create_block_candidate() {
   // 4. save block candidate
   LOG(INFO) << "saving new BlockCandidate";
   td::actor::send_closure_later(manager, &ValidatorManager::set_block_candidate, block_candidate->id,
-                                block_candidate->clone(), [self = get_self()](td::Result<td::Unit> saved) -> void {
+                                block_candidate->clone(), [self = get_self()](td::Result<td::Unit> saved)->void {
                                   LOG(DEBUG) << "got answer to set_block_candidate";
                                   td::actor::send_closure_later(std::move(self), &Collator::return_block_candidate,
                                                                 std::move(saved));
```

### validator/impl/validate-query.cpp
```diff
@@ -256,7 +256,7 @@ void ValidateQuery::start_up() {
     LOG(DEBUG) << "sending wait_block_state() query #" << i << " for " << prev_blocks[i].to_str() << " to Manager";
     ++pending;
     td::actor::send_closure_later(manager, &ValidatorManager::wait_block_state_short, prev_blocks[i], priority(),
-                                  timeout, [self = get_self(), i](td::Result<Ref<ShardState>> res) -> void {
+                                  timeout, [ self = get_self(), i ](td::Result<Ref<ShardState>> res)->void {
                                     LOG(DEBUG) << "got answer to wait_block_state_short query #" << i;
                                     td::actor::send_closure_later(
                                         std::move(self), &ValidateQuery::after_get_shard_state, i, std::move(res));
@@ -270,16 +270,16 @@ void ValidateQuery::start_up() {
   // 5. request masterchain state referred to in the block
   if (!is_masterchain()) {
     ++pending;
-    td::actor::send_closure_later(manager, &ValidatorManager::wait_block_state_short, mc_blkid_, priority(), timeout,
-                                  [self = get_self()](td::Result<Ref<ShardState>> res) {
+    td::actor::send_closure_later(manager, &ValidatorManager::wait_block_state_short, mc_blkid_, priority(),
+                                  timeout, [self = get_self()](td::Result<Ref<ShardState>> res) {
                                     LOG(DEBUG) << "got answer to wait_block_state() query for masterchain block";
                                     td::actor::send_closure_later(std::move(self), &ValidateQuery::after_get_mc_state,
                                                                   std::move(res));
                                   });
     // 5.1. request corresponding block handle
     ++pending;
-    td::actor::send_closure_later(manager, &ValidatorManager::get_block_handle, mc_blkid_, true,
-                                  [self = get_self()](td::Result<BlockHandle> res) {
+    td::actor::send_closure_later(manager, &ValidatorManager::get_block_handle, mc_blkid_,
+                                  true, [self = get_self()](td::Result<BlockHandle> res) {
                                     LOG(DEBUG) << "got answer to get_block_handle() query for masterchain block";
                                     td::actor::send_closure_later(std::move(self), &ValidateQuery::got_mc_handle,
                                                                   std::move(res));
@@ -1205,7 +1205,7 @@ bool ValidateQuery::request_neighbor_queues() {
     LOG(DEBUG) << "neighbor #" << i << " : " << descr.blk_.to_str();
     ++pending;
     send_closure_later(manager, &ValidatorManager::wait_block_message_queue_short, descr.blk_, priority(), timeout,
-                       [self = get_self(), i](td::Result<Ref<MessageQueue>> res) {
+                       [ self = get_self(), i ](td::Result<Ref<MessageQueue>> res) {
                          td::actor::send_closure(std::move(self), &ValidateQuery::got_neighbor_out_queue, i,
                                                  std::move(res));
                        });
@@ -1323,13 +1323,12 @@ bool ValidateQuery::request_aux_mc_state(BlockSeqno seqno, Ref<MasterchainStateQ
   CHECK(blkid.is_valid_ext() && blkid.is_masterchain());
   LOG(DEBUG) << "sending auxiliary wait_block_state() query for " << blkid.to_str() << " to Manager";
   ++pending;
-  td::actor::send_closure_later(manager, &ValidatorManager::wait_block_state_short, blkid, priority(), timeout,
-                                [self = get_self(), blkid](td::Result<Ref<ShardState>> res) {
-                                  LOG(DEBUG) << "got answer to wait_block_state query for " << blkid.to_str();
-                                  td::actor::send_closure_later(std::move(self),
-                                                                &ValidateQuery::after_get_aux_shard_state, blkid,
-                                                                std::move(res));
-                                });
+  td::actor::send_closure_later(manager, &ValidatorManager::wait_block_state_short, blkid, priority(), timeout, [
+    self = get_self(), blkid
+  ](td::Result<Ref<ShardState>> res) {
+    LOG(DEBUG) << "got answer to wait_block_state query for " << blkid.to_str();
+    td::actor::send_closure_later(std::move(self), &ValidateQuery::after_get_aux_shard_state, blkid, std::move(res));
+  });
   state.clear();
   return true;
 }
@@ -1668,8 +1667,8 @@ bool ValidateQuery::check_shard_layout() {
   WorkchainId wc_id{ton::workchainInvalid};
   Ref<block::WorkchainInfo> wc_info;
 
-  if (!new_shard_conf_->process_sibling_shard_hashes([self = this, &wc_set, &wc_id, &wc_info, &ccvc](
-                                                         block::McShardHash& cur, const block::McShardHash* sibling) {
+  if (!new_shard_conf_->process_sibling_shard_hashes([ self = this, &wc_set, &wc_id, &wc_info, &ccvc ](
+          block::McShardHash & cur, const block::McShardHash* sibling) {
         if (!cur.is_valid()) {
           return -2;
         }
@@ -1866,13 +1865,16 @@ bool ValidateQuery::fix_all_processed_upto() {
   if (!fix_processed_upto(*ps_.processed_upto_)) {
     return fatal_error("Cannot adjust old ProcessedUpto of our shard state");
   }
+  if (sibling_processed_upto_ && !fix_processed_upto(*sibling_processed_upto_)) {
+    return fatal_error("Cannot adjust old ProcessedUpto of the shard state of our virtual sibling");
+  }
   if (!fix_processed_upto(*ns_.processed_upto_, true)) {
     return fatal_error("Cannot adjust new ProcessedUpto of our shard state");
   }
   for (auto& descr : neighbors_) {
     CHECK(descr.processed_upto);
     if (!fix_processed_upto(*descr.processed_upto)) {
-      return fatal_error(std::string{"Cannot adjust ProcessedUpto of neighbor "} + descr.blk_.to_str());
+      return fatal_error("Cannot adjust ProcessedUpto of neighbor "s + descr.blk_.to_str());
     }
   }
   return true;
@@ -1971,6 +1973,7 @@ bool ValidateQuery::add_trivial_neighbor() {
           CHECK(found == 1);
           CHECK(after_split_);
           CHECK(sibling_out_msg_queue_);
+          CHECK(sibling_processed_upto_);
           neighbors_.emplace_back(*descr_ref);
           auto& nb2 = neighbors_.at(i);
           nb2.set_queue_root(sibling_out_msg_queue_->get_root_cell());
@@ -2327,14 +2330,14 @@ bool ValidateQuery::precheck_account_updates() {
   LOG(INFO) << "pre-checking all Account updates between the old and the new state";
   try {
     CHECK(ps_.account_dict_ && ns_.account_dict_);
-    if (!ps_.account_dict_->scan_diff(
-            *ns_.account_dict_,
-            [this](td::ConstBitPtr key, int key_len, Ref<vm::CellSlice> old_val_extra,
-                   Ref<vm::CellSlice> new_val_extra) {
-              CHECK(key_len == 256);
-              return precheck_one_account_update(key, std::move(old_val_extra), std::move(new_val_extra));
-            },
-            3 /* check augmentation of changed nodes */)) {
+    if (!ps_.account_dict_->scan_diff(*ns_.account_dict_,
+                                      [this](td::ConstBitPtr key, int key_len, Ref<vm::CellSlice> old_val_extra,
+                                             Ref<vm::CellSlice> new_val_extra) {
+                                        CHECK(key_len == 256);
+                                        return precheck_one_account_update(key, std::move(old_val_extra),
+                                                                           std::move(new_val_extra));
+                                      },
+                                      3 /* check augmentation of changed nodes */)) {
       return reject_query("invalid ShardAccounts dictionary in the new state");
     }
   } catch (vm::VmError& err) {
@@ -2688,14 +2691,14 @@ bool ValidateQuery::precheck_message_queue_update() {
   try {
     CHECK(ps_.out_msg_queue_ && ns_.out_msg_queue_);
     CHECK(out_msg_dict_);
-    if (!ps_.out_msg_queue_->scan_diff(
-            *ns_.out_msg_queue_,
-            [this](td::ConstBitPtr key, int key_len, Ref<vm::CellSlice> old_val_extra,
-                   Ref<vm::CellSlice> new_val_extra) {
-              CHECK(key_len == 352);
-              return precheck_one_message_queue_update(key, std::move(old_val_extra), std::move(new_val_extra));
-            },
-            3 /* check augmentation of changed nodes */)) {
+    if (!ps_.out_msg_queue_->scan_diff(*ns_.out_msg_queue_,
+                                       [this](td::ConstBitPtr key, int key_len, Ref<vm::CellSlice> old_val_extra,
+                                              Ref<vm::CellSlice> new_val_extra) {
+                                         CHECK(key_len == 352);
+                                         return precheck_one_message_queue_update(key, std::move(old_val_extra),
+                                                                                  std::move(new_val_extra));
+                                       },
+                                       3 /* check augmentation of changed nodes */)) {
       return reject_query("invalid OutMsgQueue dictionary in the new state");
     }
   } catch (vm::VmError& err) {
@@ -3937,6 +3940,12 @@ bool ValidateQuery::check_in_queue() {
 bool ValidateQuery::check_delivered_dequeued() {
   LOG(INFO) << "scanning new outbound queue and checking delivery status of all messages";
   bool ok = false;
+  for (const auto& nb : neighbors_) {
+    if (!nb.is_disabled() && (!nb.processed_upto || !nb.processed_upto->can_check_processed())) {
+      return fatal_error(-667, PSTRING() << "internal error: no info for checking processed messages from neighbor "
+                                         << nb.blk_.to_str());
+    }
+  }
   return ns_.out_msg_queue_->check_for_each([&](Ref<vm::CellSlice> cs_ref, td::ConstBitPtr key, int n) -> bool {
     assert(n == 352);
     // LOG(DEBUG) << "key is " << key.to_hex(n);
@@ -4674,22 +4683,21 @@ bool ValidateQuery::check_one_library_update(td::ConstBitPtr key, Ref<vm::CellSl
   } else {
     old_publishers = std::make_unique<vm::Dictionary>(256);
   }
-  if (!old_publishers->scan_diff(
-          *new_publishers,
-          [this, lib_key = key](td::ConstBitPtr key, int key_len, Ref<vm::CellSlice> old_val,
-                                Ref<vm::CellSlice> new_val) {
-            CHECK(key_len == 256);
-            if (old_val.not_null() && !old_val->empty_ext()) {
-              return false;
-            }
-            if (new_val.not_null() && !new_val->empty_ext()) {
-              return false;
-            }
-            CHECK(old_val.not_null() != new_val.not_null());
-            lib_publishers2_.emplace_back(lib_key, key, new_val.not_null());
-            return true;
-          },
-          3 /* check augmentation of changed nodes */)) {
+  if (!old_publishers->scan_diff(*new_publishers,
+                                 [ this, lib_key = key ](td::ConstBitPtr key, int key_len, Ref<vm::CellSlice> old_val,
+                                                         Ref<vm::CellSlice> new_val) {
+                                   CHECK(key_len == 256);
+                                   if (old_val.not_null() && !old_val->empty_ext()) {
+                                     return false;
+                                   }
+                                   if (new_val.not_null() && !new_val->empty_ext()) {
+                                     return false;
+                                   }
+                                   CHECK(old_val.not_null() != new_val.not_null());
+                                   lib_publishers2_.emplace_back(lib_key, key, new_val.not_null());
+                                   return true;
+                                 },
+                                 3 /* check augmentation of changed nodes */)) {
     return reject_query("invalid publishers set for shard library with hash "s + key.to_hex(256));
   }
   return true;
@@ -5011,15 +5019,14 @@ bool ValidateQuery::check_mc_state_extra() {
   try {
     vm::AugmentedDictionary old_prev_dict{old_extra.r1.prev_blocks, 32, block::tlb::aug_OldMcBlocksInfo};
     vm::AugmentedDictionary new_prev_dict{new_extra.r1.prev_blocks, 32, block::tlb::aug_OldMcBlocksInfo};
-    if (!old_prev_dict.scan_diff(
-            new_prev_dict,
-            [this](td::ConstBitPtr key, int key_len, Ref<vm::CellSlice> old_val_extra,
-                   Ref<vm::CellSlice> new_val_extra) {
-              CHECK(key_len == 32);
-              return check_one_prev_dict_update((unsigned)key.get_uint(32), std::move(old_val_extra),
-                                                std::move(new_val_extra));
-            },
-            3 /* check augmentation of changed nodes */)) {
+    if (!old_prev_dict.scan_diff(new_prev_dict,
+                                 [this](td::ConstBitPtr key, int key_len, Ref<vm::CellSlice> old_val_extra,
+                                        Ref<vm::CellSlice> new_val_extra) {
+                                   CHECK(key_len == 32);
+                                   return check_one_prev_dict_update(
+                                       (unsigned)key.get_uint(32), std::move(old_val_extra), std::move(new_val_extra));
+                                 },
+                                 3 /* check augmentation of changed nodes */)) {
       return reject_query("invalid previous block dictionary in the new state");
     }
     td::BitArray<32> key;
```
