# [?] Harden tonlib against crashes (#2406)

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2026-06-15
Source: https://github.com/ton-blockchain/ton/commit/4c92183c86f51768ca74dff02c78fae7b057f31a
Type: security-commit

## Details
Harden tonlib against crashes (#2406)

* Harden tonlib against malformed inputs

* Handle VM exceptions in SmartContract runner

* Validate tonlib log message verbosity

* Limit tonlib missing library fetches

* Harden smc-envelope message builders

* Catch exceptions at tonlib JSON boundaries

* Limit tonlib TVM stack output depth

* Retry external message packing with referenced body

* Format tonlib hardening changes

* Harden tonlib transaction list handling

* Reject invalid tonlib external messages

* Handle tonlib BOC serialization errors

* Catch tonlib proof processing exceptions

* Harden tonlib shard info proof parsing

* Formatting

---------

Co-authored-by: SpyCheese <mikle98@yandex.ru>

## Patch
### crypto/smc-envelope/GenericAccount.cpp
```diff
@@ -58,73 +58,108 @@ td::Ref<vm::Cell> GenericAccount::get_init_state(const td::Ref<vm::Cell>& code,
 }
 block::StdAddress GenericAccount::get_address(ton::WorkchainId workchain_id,
                                               const td::Ref<vm::Cell>& init_state) noexcept {
+  if (init_state.is_null()) {
+    return {};
+  }
   return block::StdAddress(workchain_id, init_state->get_hash().bits(), true /*bounce*/);
 }
 
-void GenericAccount::store_int_message(vm::CellBuilder& cb, const block::StdAddress& dest_address, td::int64 gramms,
+bool GenericAccount::store_int_message(vm::CellBuilder& cb, const block::StdAddress& dest_address, td::int64 gramms,
                                        td::Ref<vm::Cell> extra_currencies) {
   td::BigInt256 dest_addr;
   dest_addr.import_bits(dest_address.addr.as_bitslice());
-  cb.store_zeroes(1)
-      .store_ones(1)
-      .store_long(dest_address.bounceable, 1)
-      .store_zeroes(3)
-      .store_ones(1)
-      .store_zeroes(2)
-      .store_long(dest_address.workchain, 8)
-      .store_int256(dest_addr, 256);
-  block::tlb::t_Grams.store_integer_value(cb, td::BigInt256(gramms));
-  cb.store_maybe_ref(extra_currencies);
-  cb.store_zeroes(8 + 64 + 32);
+  return cb.store_zeroes_bool(1) && cb.store_ones_bool(1) && cb.store_long_bool(dest_address.bounceable, 1) &&
+         cb.store_zeroes_bool(3) && cb.store_ones_bool(1) && cb.store_zeroes_bool(2) &&
+         cb.store_long_bool(dest_address.workchain, 8) && cb.store_int256_bool(dest_addr, 256) &&
+         block::tlb::t_Grams.store_integer_value(cb, td::BigInt256(gramms)) && cb.store_maybe_ref(extra_currencies) &&
+         cb.store_zeroes_bool(8 + 64 + 32);
 }
 
 td::Ref<vm::Cell> GenericAccount::create_ext_message(const block::StdAddress& address, td::Ref<vm::Cell> new_state,
                                                      td::Ref<vm::Cell> body) noexcept {
+  if (body.is_null()) {
+    return {};
+  }
   block::gen::Message::Record message;
   /*info*/ {
     block::gen::CommonMsgInfo::Record_ext_in_msg_info info;
     /* src */
-    tlb::csr_pack(info.src, block::gen::MsgAddressExt::Record_addr_none{});
+    if (!tlb::csr_pack(info.src, block::gen::MsgAddressExt::Record_addr_none{})) {
+      return {};
+    }
     /* dest */ {
       block::gen::MsgAddressInt::Record_addr_std dest;
-      dest.anycast = vm::CellBuilder().store_zeroes(1).as_cellslice_ref();
+      vm::CellBuilder anycast;
+      if (!anycast.store_zeroes_bool(1)) {
+        return {};
+      }
+      dest.anycast = anycast.as_cellslice_ref();
       dest.workchain_id = address.workchain;
       dest.address = address.addr;
 
-      tlb::csr_pack(info.dest, dest);
+      if (!tlb::csr_pack(info.dest, dest)) {
+        return {};
+      }
     }
     /* import_fee */ {
       vm::CellBuilder cb;
-      block::tlb::t_Grams.store_integer_value(cb, td::BigInt256(0));
+      if (!block::tlb::t_Grams.store_integer_value(cb, td::BigInt256(0))) {
+        return {};
+      }
       info.import_fee = cb.as_cellslice_ref();
     }
 
-    tlb::csr_pack(message.info, info);
+    if (!tlb::csr_pack(message.info, info)) {
+      return {};
+    }
   }
   /* init */ {
     if (new_state.not_null()) {
       // Just(Left(new_state))
-      message.init = vm::CellBuilder()
-                         .store_ones(1)
-                         .store_zeroes(1)
-                         .append_cellslice(vm::load_cell_slice(new_state))
-                         .as_cellslice_ref();
+      vm::CellBuilder cb;
+      auto init = vm::load_cell_slice(new_state);
+      if (!(cb.store_ones_bool(1) && cb.store_zeroes_bool(1) && cb.append_cellslice_bool(init))) {
+        return {};
+      }
+      message.init = cb.as_cellslice_ref();
     } else {
-      message.init = vm::CellBuilder().store_zeroes(1).as_cellslice_ref();
-      CHECK(message.init.not_null());
+      vm::CellBuilder cb;
+      if (!cb.store_zeroes_bool(1)) {
+        return {};
+      }
+      message.init = cb.as_cellslice_ref();
     }
   }
+  bool body_stored_by_ref = false;
   /* body */ {
-    message.body = vm::CellBuilder().store_zeroes(1).append_cellslice(vm::load_cell_slice_ref(body)).as_cellslice_ref();
+    vm::CellBuilder cb;
+    auto body_slice = vm::load_cell_slice_ref(body);
+    if (body_slice.not_null() && cb.can_extend_by(1 + body_slice->size(), body_slice->size_refs())) {
+      if (!(cb.store_zeroes_bool(1) && cb.append_cellslice_bool(body_slice))) {
+        return {};
+      }
+    } else if (!(cb.store_ones_bool(1) && cb.store_ref_bool(body))) {
+      return {};
+    } else {
+      body_stored_by_ref = true;
+    }
+    message.body = cb.as_cellslice_ref();
   }
 
   td::Ref<vm::Cell> res;
-  tlb::type_pack_cell(res, block::gen::t_Message_Any, message);
-  if (res.is_null()) {
-    /* body */ { message.body = vm::CellBuilder().store_ones(1).store_ref(std::move(body)).as_cellslice_ref(); }
-    tlb::type_pack_cell(res, block::gen::t_Message_Any, message);
+  if (!tlb::type_pack_cell(res, block::gen::t_Message_Any, message) || res.is_null()) {
+    if (body_stored_by_ref) {
+      return {};
+    }
+    vm::CellBuilder ref_body;
+    if (!(ref_body.store_ones_bool(1) && ref_body.store_ref_bool(body))) {
+      return {};
+    }
+    message.body = ref_body.as_cellslice_ref();
+    if (!tlb::type_pack_cell(res, block::gen::t_Message_Any, message) || res.is_null()) {
+      return {};
+    }
   }
-  CHECK(res.not_null());
 
   return res;
 }
```

### crypto/smc-envelope/GenericAccount.h
```diff
@@ -37,7 +37,7 @@ class GenericAccount {
   static block::StdAddress get_address(ton::WorkchainId workchain_id, const td::Ref<vm::Cell>& init_state) noexcept;
   static td::Ref<vm::Cell> create_ext_message(const block::StdAddress& address, td::Ref<vm::Cell> new_state,
                                               td::Ref<vm::Cell> body) noexcept;
-  static void store_int_message(vm::CellBuilder& cb, const block::StdAddress& dest_address, td::int64 gramms,
+  static bool store_int_message(vm::CellBuilder& cb, const block::StdAddress& dest_address, td::int64 gramms,
                                 td::Ref<vm::Cell> extra_currencies);
 
   static td::Result<td::Ed25519::PublicKey> get_public_key(const SmartContract& sc);
```

### crypto/smc-envelope/HighloadWallet.cpp
```diff
@@ -32,15 +32,17 @@ td::Result<td::Ref<vm::Cell>> HighloadWallet::make_a_gift_message(const td::Ed25
                                                                   td::uint32 valid_until, td::Span<Gift> gifts) const {
   TRY_RESULT(wallet_id, get_wallet_id());
   TRY_RESULT(seqno, get_seqno());
-  CHECK(gifts.size() <= get_max_gifts_size());
+  if (gifts.size() > get_max_gifts_size()) {
+    return td::Status::Error("Too many messages");
+  }
   vm::Dictionary messages(16);
   for (size_t i = 0; i < gifts.size(); i++) {
     auto& gift = gifts[i];
     td::int32 send_mode = 3;
     if (gift.gramms == -1) {
       send_mode += 128;
     }
-    auto message_inner = create_int_message(gift);
+    TRY_RESULT(message_inner, try_create_int_message(gift));
     vm::CellBuilder cb;
     cb.store_long(send_mode, 8).store_ref(message_inner);
     auto key = messages.integer_key(td::make_refint(i), 16, false);
@@ -49,9 +51,11 @@ td::Result<td::Ref<vm::Cell>> HighloadWallet::make_a_gift_message(const td::Ed25
 
   vm::CellBuilder cb;
   cb.store_long(wallet_id, 32).store_long(valid_until, 32).store_long(seqno, 32);
-  CHECK(cb.store_maybe_ref(messages.get_root_cell()));
+  if (!cb.store_maybe_ref(messages.get_root_cell())) {
+    return td::Status::Error("Failed to store highload wallet messages");
+  }
   auto message_outer = cb.finalize();
-  auto signature = private_key.sign(message_outer->get_hash().as_slice()).move_as_ok();
+  TRY_RESULT(signature, private_key.sign(message_outer->get_hash().as_slice()));
   return vm::CellBuilder().store_bytes(signature).append_cellslice(vm::load_cell_slice(message_outer)).finalize();
 }
 
```

### crypto/smc-envelope/HighloadWalletV2.cpp
```diff
@@ -32,52 +32,68 @@ td::Result<td::Ref<vm::Cell>> HighloadWalletV2::get_init_message(const td::Ed255
                                                                  td::uint32 valid_until) const noexcept {
   TRY_RESULT(wallet_id, get_wallet_id());
   td::uint32 id = -1;
-  auto append_message = [&](auto&& cb) -> vm::CellBuilder& {
-    cb.store_long(wallet_id, 32).store_long(valid_until, 32).store_long(id, 32);
-    CHECK(cb.store_maybe_ref({}));
-    return cb;
+  auto make_message = [&](td::Slice signature) -> td::Result<td::Ref<vm::Cell>> {
+    vm::CellBuilder cb;
+    if (!signature.empty()) {
+      cb.store_bytes(signature);
+    }
+    if (!(cb.store_long_bool(wallet_id, 32) && cb.store_long_bool(valid_until, 32) && cb.store_long_bool(id, 32) &&
+          cb.store_maybe_ref({}))) {
+      return td::Status::Error("Failed to store highload wallet init message");
+    }
+    return cb.finalize();
   };
-  auto signature = private_key.sign(append_message(vm::CellBuilder()).finalize()->get_hash().as_slice()).move_as_ok();
+  TRY_RESULT(unsigned_message, make_message({}));
+  TRY_RESULT(signature, private_key.sign(unsigned_message->get_hash().as_slice()));
 
-  return append_message(vm::CellBuilder().store_bytes(signature)).finalize();
+  return make_message(signature.as_slice());
 }
 
 td::Result<td::Ref<vm::Cell>> HighloadWalletV2::make_a_gift_message(const td::Ed25519::PrivateKey& private_key,
                                                                     td::uint32 valid_until,
                                                                     td::Span<Gift> gifts) const {
   TRY_RESULT(wallet_id, get_wallet_id());
-  CHECK(gifts.size() <= get_max_gifts_size());
+  if (gifts.size() > get_max_gifts_size()) {
+    return td::Status::Error("Too many messages");
+  }
   vm::Dictionary messages(16);
   for (size_t i = 0; i < gifts.size(); i++) {
     auto& gift = gifts[i];
     td::int32 send_mode = 3;
     if (gift.gramms == -1) {
       send_mode += 128;
     }
+    TRY_RESULT(message, try_create_int_message(gift));
     vm::CellBuilder cb;
-    cb.store_long(send_mode, 8).store_ref(create_int_message(gift));
+    cb.store_long(send_mode, 8).store_ref(std::move(message));
     auto key = messages.integer_key(td::make_refint(i), 16, false);
     messages.set_builder(key.bits(), 16, cb);
   }
   std::string hash;
   {
     vm::CellBuilder cb;
-    CHECK(cb.store_maybe_ref(messages.get_root_cell()));
+    if (!cb.store_maybe_ref(messages.get_root_cell())) {
+      return td::Status::Error("Failed to store highload wallet messages hash");
+    }
     hash = cb.finalize()->get_hash().as_slice().substr(28, 4).str();
   }
 
   vm::CellBuilder cb;
   cb.store_long(wallet_id, 32).store_long(valid_until, 32).store_bytes(hash);
-  CHECK(cb.store_maybe_ref(messages.get_root_cell()));
+  if (!cb.store_maybe_ref(messages.get_root_cell())) {
+    return td::Status::Error("Failed to store highload wallet messages");
+  }
   auto message_outer = cb.finalize();
-  auto signature = private_key.sign(message_outer->get_hash().as_slice()).move_as_ok();
+  TRY_RESULT(signature, private_key.sign(message_outer->get_hash().as_slice()));
   return vm::CellBuilder().store_bytes(signature).append_cellslice(vm::load_cell_slice(message_outer)).finalize();
 }
 
 td::Ref<vm::Cell> HighloadWalletV2::get_init_data(const InitData& init_data) noexcept {
   vm::CellBuilder cb;
   cb.store_long(init_data.wallet_id, 32).store_long(init_data.seqno, 64).store_bytes(init_data.public_key);
-  CHECK(cb.store_maybe_ref({}));
+  if (!cb.store_maybe_ref({})) {
+    return {};
+  }
   return cb.finalize();
 }
 
```

### crypto/smc-envelope/ManualDns.cpp
```diff
@@ -38,9 +38,14 @@ td::StringBuilder& operator<<(td::StringBuilder& sb, const ManualDns::EntryData&
     case ManualDns::EntryData::Type::NextResolver:
       return sb << "NEXT:" << data.data.get<ManualDns::EntryDataNextResolver>().resolver.rserialize();
     case ManualDns::EntryData::Type::AdnlAddress:
-      return sb << "ADNL:"
-                << td::adnl_id_encode(data.data.get<ManualDns::EntryDataAdnlAddress>().adnl_address.as_slice())
-                       .move_as_ok();
+      sb << "ADNL:";
+      {
+        auto encoded = td::adnl_id_encode(data.data.get<ManualDns::EntryDataAdnlAddress>().adnl_address.as_slice());
+        if (encoded.is_error()) {
+          return sb << "<invalid>";
+        }
+        return sb << encoded.move_as_ok();
+      }
     case ManualDns::EntryData::Type::SmcAddress:
       return sb << "SMC:" << data.data.get<ManualDns::EntryDataSmcAddress>().smc_address.rserialize();
     case ManualDns::EntryData::Type::StorageAddress:
@@ -69,33 +74,43 @@ td::Result<td::Ref<vm::Cell>> DnsInterface::EntryData::as_cell() const {
         vm::CellBuilder cb;
         vm::CellText::store(cb, text.text);
         dns.x = vm::load_cell_slice_ref(cb.finalize());
-        tlb::pack_cell(res, dns);
+        if (!tlb::pack_cell(res, dns)) {
+          error = td::Status::Error("Failed to pack dns_text");
+        }
       },
       [&](const EntryDataNextResolver& resolver) {
         block::gen::DNSRecord::Record_dns_next_resolver dns;
         vm::CellBuilder cb;
         block::tlb::t_MsgAddressInt.store_std_address(cb, resolver.resolver.workchain, resolver.resolver.addr);
         dns.resolver = vm::load_cell_slice_ref(cb.finalize());
-        tlb::pack_cell(res, dns);
+        if (!tlb::pack_cell(res, dns)) {
+          error = td::Status::Error("Failed to pack dns_next_resolver");
+        }
       },
       [&](const EntryDataAdnlAddress& adnl_address) {
         block::gen::DNSRecord::Record_dns_adnl_address dns;
         dns.adnl_addr = adnl_address.adnl_address;
         dns.flags = 0;
-        tlb::pack_cell(res, dns);
+        if (!tlb::pack_cell(res, dns)) {
+          error = td::Status::Error("Failed to pack dns_adnl_address");
+        }
       },
       [&](const EntryDataSmcAddress& smc_address) {
         block::gen::DNSRecord::Record_dns_smc_address dns;
         vm::CellBuilder cb;
         block::tlb::t_MsgAddressInt.store_std_address(cb, smc_address.smc_address.workchain,
                                                       smc_address.smc_address.addr);
         dns.smc_addr = vm::load_cell_slice_ref(cb.finalize());
-        tlb::pack_cell(res, dns);
+        if (!tlb::pack_cell(res, dns)) {
+          error = td::Status::Error("Failed to pack dns_smc_address");
+        }
       },
       [&](const EntryDataStorageAddress& storage_address) {
         block::gen::DNSRecord::Record_dns_storage_address dns;
         dns.bag_id = storage_address.bag_id;
-        tlb::pack_cell(res, dns);
+        if (!tlb::pack_cell(res, dns)) {
+          error = td::Status::Error("Failed to pack dns_storage_address");
+        }
       }));
   if (error.is_error()) {
     return error;
@@ -260,6 +275,9 @@ td::Result<td::uint32> ManualDns::get_wallet_id_or_throw() const {
 
 td::Result<td::Ref<vm::Cell>> ManualDns::create_set_value_unsigned(td::Bits256 category, td::Slice name,
                                                                    td::Ref<vm::Cell> data) const {
+  if (name.size() > 127) {
+    return td::Status::Error("DNS encoded name is too long");
+  }
   //11 VSet: set specified value to specified subdomain->category (x=2)
   //[Int<256b>:category] [Name<?>:subdomain] [Cell<1r>:value]
   vm::CellBuilder cb;
@@ -274,10 +292,15 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_set_value_unsigned(td::Bits256 c
     cb.store_long(1, 1);
     cb.store_ref(vm::CellBuilder().store_bytes(name).finalize());
   }
-  cb.store_maybe_ref(std::move(data));
+  if (!cb.store_maybe_ref(std::move(data))) {
+    return td::Status::Error("Failed to store DNS record data");
+  }
   return cb.finalize();
 }
 td::Result<td::Ref<vm::Cell>> ManualDns::create_delete_value_unsigned(td::Bits256 category, td::Slice name) const {
+  if (name.size() > 127) {
+    return td::Status::Error("DNS encoded name is too long");
+  }
   //12 VDel: delete specified subdomain->category (x=2)
   //[Int<256b>:category] [Name<?>:subdomain]
   vm::CellBuilder cb;
@@ -306,13 +329,20 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_set_all_unsigned(td::Span<Action
   vm::PrefixDictionary pdict(1023);
   for (auto& action : entries) {
     auto name_key = encode_name(action.name);
+    if (name_key.size() > 127) {
+      return td::Status::Error("DNS encoded name is too long");
+    }
     int zero_cnt = 0;
     for (auto c : name_key) {
       if (c == 0) {
         zero_cnt++;
       }
     }
-    auto new_name_key = vm::load_cell_slice(vm::CellBuilder().store_long(zero_cnt, 7).store_bytes(name_key).finalize());
+    vm::CellBuilder key_builder;
+    if (!(key_builder.store_long_bool(zero_cnt, 7) && key_builder.store_bytes_bool(name_key))) {
+      return td::Status::Error("Failed to store DNS name key");
+    }
+    auto new_name_key = vm::load_cell_slice(key_builder.finalize());
     auto ptr = new_name_key.data_bits();
     auto ptr_size = new_name_key.size();
     auto o_dict = pdict.lookup(ptr, ptr_size);
@@ -321,7 +351,10 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_set_all_unsigned(td::Span<Action
       o_dict->prefetch_maybe_ref(dict_root);
     }
     vm::Dictionary dict(dict_root, 256);
-    if (!action.data.value().is_null()) {
+    if (!action.data || !action.data.value().is_null()) {
+      if (!action.data) {
+        return td::Status::Error("DNS action data is empty");
+      }
       dict.set_ref(action.category.bits(), 256, action.data.value());
     }
     pdict.set(ptr, ptr_size, dict.get_root());
@@ -330,7 +363,9 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_set_all_unsigned(td::Span<Action
   vm::CellBuilder cb;
   cb.store_long(31, 6);
 
-  cb.store_maybe_ref(pdict.get_root_cell());
+  if (!cb.store_maybe_ref(pdict.get_root_cell())) {
+    return td::Status::Error("Failed to store DNS domain table");
+  }
 
   return cb.finalize();
 }
@@ -340,6 +375,9 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_set_all_unsigned(td::Span<Action
 //22 DDel: delete entire category dictionary of specified domain (x=0)
 //[Name<?>:subdomain]
 td::Result<td::Ref<vm::Cell>> ManualDns::create_delete_name_unsigned(td::Slice name) const {
+  if (name.size() > 127) {
+    return td::Status::Error("DNS encoded name is too long");
+  }
   vm::CellBuilder cb;
   cb.store_long(22, 6);
   if (name.size() <= 58) {
@@ -353,6 +391,9 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_delete_name_unsigned(td::Slice n
   return cb.finalize();
 }
 td::Result<td::Ref<vm::Cell>> ManualDns::create_set_name_unsigned(td::Slice name, td::Span<Action> entries) const {
+  if (name.size() > 127) {
+    return td::Status::Error("DNS encoded name is too long");
+  }
   vm::CellBuilder cb;
   cb.store_long(21, 6);
   if (name.size() <= 58) {
@@ -367,40 +408,57 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_set_name_unsigned(td::Slice name
   vm::Dictionary dict(256);
 
   for (auto& action : entries) {
+    if (!action.data) {
+      return td::Status::Error("DNS action data is empty");
+    }
     if (action.data.value().is_null()) {
       continue;
     }
     dict.set_ref(action.category.cbits(), 256, action.data.value());
   }
-  cb.store_maybe_ref(dict.get_root_cell());
+  if (!cb.store_maybe_ref(dict.get_root_cell())) {
+    return td::Status::Error("Failed to store DNS category table");
+  }
 
   return cb.finalize();
 }
 
 td::Result<td::Ref<vm::Cell>> ManualDns::prepare(td::Ref<vm::Cell> data, td::uint32 valid_until) const {
+  if (data.is_null()) {
+    return td::Status::Error("DNS query body is empty");
+  }
   TRY_RESULT(wallet_id, get_wallet_id());
   auto hash = data->get_hash().as_slice().substr(28, 4).str();
 
   vm::CellBuilder cb;
-  cb.store_long(wallet_id, 32).store_long(valid_until, 32);
+  if (!(cb.store_long_bool(wallet_id, 32) && cb.store_long_bool(valid_until, 32))) {
+    return td::Status::Error("Failed to store DNS query header");
+  }
   //cb.store_bytes(hash);
-  cb.store_long(td::Random::secure_uint32(), 32);
-  cb.append_cellslice(vm::load_cell_slice(data));
+  if (!(cb.store_long_bool(td::Random::secure_uint32(), 32) && cb.append_cellslice_bool(vm::load_cell_slice(data)))) {
+    return td::Status::Error("Failed to store DNS query body");
+  }
   return cb.finalize();
 }
 
 td::Result<td::Ref<vm::Cell>> ManualDns::sign(const td::Ed25519::PrivateKey& private_key, td::Ref<vm::Cell> data) {
-  auto signature = private_key.sign(data->get_hash().as_slice()).move_as_ok();
+  if (data.is_null()) {
+    return td::Status::Error("DNS query body is empty");
+  }
+  TRY_RESULT(signature, private_key.sign(data->get_hash().as_slice()));
   vm::CellBuilder cb;
-  cb.store_bytes(signature.as_slice());
-  cb.append_cellslice(vm::load_cell_slice(data));
+  if (!(cb.store_bytes_bool(signature.as_slice()) && cb.append_cellslice_bool(vm::load_cell_slice(data)))) {
+    return td::Status::Error("Failed to store signed DNS query");
+  }
   return cb.finalize();
 }
 
 td::Result<td::Ref<vm::Cell>> ManualDns::create_init_query(const td::Ed25519::PrivateKey& private_key,
                                                            td::uint32 valid_until) const {
   vm::CellBuilder cb;
-  cb.store_long(0, 6);
+  if (!cb.store_long_bool(0, 6)) {
+    return td::Status::Error("Failed to store DNS init query");
+  }
 
   TRY_RESULT(prepared, prepare(cb.finalize(), valid_until));
   return sign(private_key, std::move(prepared));
@@ -409,8 +467,9 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_init_query(const td::Ed25519::Pr
 td::Ref<vm::Cell> ManualDns::create_init_data_fast(const td::Ed25519::PublicKey& public_key, td::uint32 wallet_id) {
   vm::CellBuilder cb;
   cb.store_long(wallet_id, 32).store_long(0, 64).store_bytes(public_key.as_octet_string());
-  CHECK(cb.store_maybe_ref({}));
-  CHECK(cb.store_maybe_ref({}));
+  if (!(cb.store_maybe_ref({}) && cb.store_maybe_ref({}))) {
+    return {};
+  }
   return cb.finalize();
 }
 
@@ -450,15 +509,23 @@ td::Result<std::vector<ManualDns::RawEntry>> ManualDns::resolve_raw_or_throw(td:
   } else {
     if (category.is_zero()) {
       vm::Dictionary dict(std::move(data), 256);
-      dict.check_for_each([&](td::Ref<vm::CellSlice> cs, td::ConstBitPtr key, int n) {
-        CHECK(n == 256);
-        if (cs.is_null() || cs->size_ext() != 0x10000) {
-          return true;
-        }
-        cs = vm::load_cell_slice_ref(cs->prefetch_ref());
-        vec.push_back({name.str(), td::Bits256(key), cs});
-        return true;
-      });
+      if (!dict.check_for_each([&](td::Ref<vm::CellSlice> cs, td::ConstBitPtr key, int n) {
+            if (n != 256) {
+              return false;
+            }
+            if (cs.is_null() || cs->size_ext() != 0x10000) {
+              return true;
+            }
+            auto value = cs->prefetch_ref();
+            if (value.is_null()) {
+              return false;
+            }
+            cs = vm::load_cell_slice_ref(std::move(value));
+            vec.push_back({name.str(), td::Bits256(key), cs});
+            return true;
+          })) {
+        return td::Status::Error("Invalid DNS category dictionary");
+      }
     } else {
       vec.push_back({name.str(), category, vm::load_cell_slice_ref(data)});
     }
@@ -480,7 +547,9 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_update_query(CombinedActions<Act
     }
     return create_set_name_unsigned(encode_name(combined.name), combined.actions.value());
   }
-  CHECK(combined.actions.value().size() == 1);
+  if (!combined.actions || combined.actions.value().size() != 1) {
+    return td::Status::Error("DNS update query has invalid action count");
+  }
   auto& action = combined.actions.value()[0];
   if (action.data) {
     return create_set_value_unsigned(action.category, encode_name(action.name), action.data.value());
@@ -500,14 +569,24 @@ td::Result<td::Ref<vm::Cell>> ManualDns::create_update_query(td::Ed25519::Privat
 
   td::Ref<vm::Cell> combined_query;
   for (auto& query : td::reversed(queries)) {
+    if (query.is_null()) {
+      return td::Status::Error("DNS update query is empty");
+    }
     if (combined_query.is_null()) {
       combined_query = std::move(query);
     } else {
       auto next = vm::load_cell_slice(combined_query);
-      combined_query = vm::CellBuilder()
-                           .append_cellslice(vm::load_cell_slice(query))
-                           .store_ref(vm::CellBuilder().append_cellslice(next).finalize())
-                           .finalize();
+      vm::CellBuilder next_builder;
+      if (!next_builder.append_cellslice_bool(next)) {
+        return td::Status::Error("Failed to store chained DNS query");
+      }
+      auto next_cell = next_builder.finalize();
+      vm::CellBuilder query_builder;
+      if (!(query_builder.append_cellslice_bool(vm::load_cell_slice(query)) &&
+            query_builder.store_ref_bool(std::move(next_cell)))) {
+        return td::Status::Error("Failed to chain DNS update query");
+      }
+      combined_query = query_builder.finalize();
     }
   }
 
```

### crypto/smc-envelope/ManualDns.h
```diff
@@ -143,18 +143,21 @@ class DnsInterface {
     td::optional<td::Ref<vm::Cell>> data;
 
     bool does_create_category() const {
-      CHECK(!name.empty());
-      CHECK(!category.is_zero());
+      if (name.empty() || category.is_zero()) {
+        return false;
+      }
       return static_cast<bool>(data);
     }
     bool does_change_empty() const {
-      CHECK(!name.empty());
-      CHECK(!category.is_zero());
+      if (name.empty() || category.is_zero()) {
+        return false;
+      }
       return static_cast<bool>(data) && data.value().not_null();
     }
     void make_non_empty() {
-      CHECK(!name.empty());
-      CHECK(!category.is_zero());
+      if (name.empty() || category.is_zero()) {
+        return;
+      }
       if (!data) {
         data = td::Ref<vm::Cell>();
       }
```

### crypto/smc-envelope/MultisigWallet.cpp
```diff
@@ -33,30 +33,50 @@ MultisigWallet::QueryBuilder::QueryBuilder(td::uint32 wallet_id, td::int64 query
              .finalize();
 }
 void MultisigWallet::QueryBuilder::sign(td::int32 id, td::Ed25519::PrivateKey& pk) {
-  CHECK(id < td::narrow_cast<td::int32>(mask_.size()));
-  auto signature = pk.sign(msg_->get_hash().as_slice()).move_as_ok();
+  if (id < 0 || id >= td::narrow_cast<td::int32>(mask_.size()) || msg_.is_null()) {
+    return;
+  }
+  auto r_signature = pk.sign(msg_->get_hash().as_slice());
+  if (r_signature.is_error()) {
+    return;
+  }
+  auto signature = r_signature.move_as_ok();
   mask_.set(id);
   vm::CellBuilder cb;
   cb.store_bytes(signature.as_slice());
   cb.store_long(id, 8);
-  cb.ensure_throw(cb.store_maybe_ref(std::move(dict_)));
+  if (!cb.store_maybe_ref(std::move(dict_))) {
+    return;
+  }
   dict_ = cb.finalize();
 }
 
 td::Ref<vm::Cell> MultisigWallet::QueryBuilder::create_inner() const {
+  if (msg_.is_null()) {
+    return {};
+  }
   vm::CellBuilder cb;
-  cb.ensure_throw(cb.store_maybe_ref(dict_));
+  if (!cb.store_maybe_ref(dict_)) {
+    return {};
+  }
   return cb.append_cellslice(vm::load_cell_slice(msg_)).finalize();
 }
 
 td::Ref<vm::Cell> MultisigWallet::QueryBuilder::create(td::int32 id, td::Ed25519::PrivateKey& pk) const {
   auto cell = create_inner();
+  if (cell.is_null()) {
+    return {};
+  }
   vm::CellBuilder cb;
   cb.store_long(id, 8);
   cb.append_cellslice(vm::load_cell_slice(cell));
   cell = cb.finalize();
 
-  auto signature = pk.sign(cell->get_hash().as_slice()).move_as_ok();
+  auto r_signature = pk.sign(cell->get_hash().as_slice());
+  if (r_signature.is_error()) {
+    return {};
+  }
+  auto signature = r_signature.move_as_ok();
   vm::CellBuilder cb2;
   cb2.store_bytes(signature.as_slice());
   cb2.append_cellslice(vm::load_cell_slice(cell));
@@ -118,7 +138,9 @@ td::Ref<vm::Cell> MultisigWallet::create_init_data(td::uint32 wallet_id, std::ve
   }
   auto res = run_get_method("create_init_state", {td::make_refint(wallet_id), td::make_refint(public_keys.size()),
                                                   td::make_refint(k), pk.get_root_cell()});
-  CHECK(res.code == 0);
+  if (res.code != 0 || res.stack.is_null()) {
+    return {};
+  }
   return res.stack.write().pop_cell();
 }
 
@@ -133,8 +155,9 @@ td::Ref<vm::Cell> MultisigWallet::create_init_data_fast(td::uint32 wallet_id, st
   vm::CellBuilder cb;
   cb.store_long(wallet_id, 32);
   cb.store_long(public_keys.size(), 8).store_long(k, 8).store_long(0, 64);
-  cb.ensure_throw(cb.store_maybe_ref(pk.get_root_cell()));
-  cb.ensure_throw(cb.store_maybe_ref({}));
+  if (!(cb.store_maybe_ref(pk.get_root_cell()) && cb.store_maybe_ref({}))) {
+    return {};
+  }
   return cb.finalize();
 }
 
```

### crypto/smc-envelope/PaymentChannel.cpp
```diff
@@ -52,7 +52,9 @@ td::Ref<vm::Cell> Config::serialize() const {
   rec.min_A_extra = pack_grams(min_A_extra);
 
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 
@@ -65,7 +67,9 @@ td::Ref<vm::Cell> MsgInit::serialize() const {
   rec.channel_id = channel_id;
 
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 
@@ -75,24 +79,39 @@ td::Ref<vm::Cell> Promise::serialize() const {
   rec.promise_A = pack_grams(promise_A);
   rec.promise_B = pack_grams(promise_B);
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 
 td::SecureString sign(const td::Ref<vm::Cell>& msg, const td::Ed25519::PrivateKey* key) {
-  return key->sign(msg->get_hash().as_slice()).move_as_ok();
+  if (!key || msg.is_null()) {
+    return {};
+  }
+  auto r_signature = key->sign(msg->get_hash().as_slice());
+  if (r_signature.is_error()) {
+    return {};
+  }
+  return r_signature.move_as_ok();
 }
 
 td::Ref<vm::Cell> maybe_sign(const td::Ref<vm::Cell>& msg, const td::Ed25519::PrivateKey* key) {
   if (!key) {
     return {};
   }
-  return vm::CellBuilder().store_bytes(sign(msg, key).as_slice()).finalize();
+  auto signature = sign(msg, key);
+  if (signature.empty()) {
+    return {};
+  }
+  return vm::CellBuilder().store_bytes(signature.as_slice()).finalize();
 }
 
 td::Ref<vm::CellSlice> maybe_ref(td::Ref<vm::Cell> msg) {
   vm::CellBuilder cb;
-  CHECK(cb.store_maybe_ref(msg));
+  if (!cb.store_maybe_ref(msg)) {
+    return {};
+  }
   return vm::load_cell_slice_ref(cb.finalize());
 }
 
@@ -103,43 +122,61 @@ td::Ref<vm::Cell> MsgClose::serialize() const {
   rec.promise = signed_promise;
 
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 
 td::Ref<vm::Cell> MsgTimeout::serialize() const {
   block::gen::ChanMsg::Record_chan_msg_timeout rec;
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 
 td::Ref<vm::Cell> MsgPayout::serialize() const {
   block::gen::ChanMsg::Record_chan_msg_payout rec;
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 
 td::SecureString SignedPromise::signature(const td::Ed25519::PrivateKey* key, const td::Ref<vm::Cell>& promise) {
   return sign(promise, key);
 }
 td::Ref<vm::Cell> SignedPromise::create_and_serialize(td::Slice signature, const td::Ref<vm::Cell>& promise) {
+  if (promise.is_null()) {
+    return {};
+  }
   block::gen::ChanSignedPromise::Record rec;
   rec.promise = vm::load_cell_slice_ref(promise);
-  LOG(ERROR) << "signature.size() = " << signature.size();
+  if (signature.size() != 64) {
+    return {};
+  }
   rec.sig = maybe_ref(vm::CellBuilder().store_bytes(signature).finalize());
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 td::Ref<vm::Cell> SignedPromise::create_and_serialize(const td::Ed25519::PrivateKey* key,
                                                       const td::Ref<vm::Cell>& promise) {
+  if (promise.is_null()) {
+    return {};
+  }
   block::gen::ChanSignedPromise::Record rec;
   rec.promise = vm::load_cell_slice_ref(promise);
   rec.sig = maybe_ref(maybe_sign(promise, key));
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 
@@ -148,6 +185,9 @@ bool SignedPromise::unpack(td::Ref<vm::Cell> cell) {
   if (!tlb::unpack_cell(cell, rec)) {
     return false;
   }
+  if (rec.promise.is_null() || rec.sig.is_null()) {
+    return false;
+  }
   block::gen::ChanPromise::Record rec_promise;
   if (!tlb::csr_unpack(rec.promise, rec_promise)) {
     return false;
@@ -163,9 +203,12 @@ bool SignedPromise::unpack(td::Ref<vm::Cell> cell) {
   if (!rec.sig->prefetch_maybe_ref(sig_cell)) {
     return false;
   }
+  if (sig_cell.is_null()) {
+    return false;
+  }
   td::SecureString signature(64);
   vm::CellSlice cs = vm::load_cell_slice(sig_cell);
-  if (!cs.prefetch_bytes(signature.as_mutable_slice())) {
+  if (!cs.prefetch_bytes(signature.as_mutable_slice()) || !cs.empty_ext()) {
     return false;
   }
   o_signature = std::move(signature);
@@ -182,7 +225,9 @@ td::Ref<vm::Cell> StateInit::serialize() const {
   rec.signed_A = signed_A;
   rec.signed_B = signed_B;
   td::Ref<vm::Cell> res;
-  CHECK(tlb::pack_cell(res, rec));
+  if (!tlb::pack_cell(res, rec)) {
+    return {};
+  }
   return res;
 }
 
@@ -191,7 +236,9 @@ td::Ref<vm::Cell> Data::serialize() const {
   rec.config = config;
   rec.state = state;
   td::Ref<vm::Cell> res;
-  CHECK(block::gen::t_ChanData.cell_pack(res, rec));
+  if (!block::gen::t_ChanData.cell_pack(res, rec)) {
+    return {};
+  }
   return res;
 }
 
```

### crypto/smc-envelope/PaymentChannel.h
```diff
@@ -145,14 +145,20 @@ struct MsgBuilder {
   td::Ref<vm::Cell> finalize() && {
     block::gen::ChanSignedMsg::Record rec;
     auto msg = static_cast<T&&>(*this).msg.serialize();
+    if (msg.is_null()) {
+      return {};
+    }
     rec.msg = vm::load_cell_slice_ref(msg);
     rec.sig_A = maybe_ref(maybe_sign(msg, a_key));
     rec.sig_B = maybe_ref(maybe_sign(msg, b_key));
     block::gen::ChanOp::Record op_rec;
-    CHECK(tlb::csr_pack(op_rec.msg, rec));
-    LOG(ERROR) << op_rec.msg->size();
+    if (!tlb::csr_pack(op_rec.msg, rec)) {
+      return {};
+    }
     td::Ref<vm::Cell> res;
-    CHECK(tlb::pack_cell(res, op_rec));
+    if (!tlb::pack_cell(res, op_rec)) {
+      return {};
+    }
     return res;
   }
 };
@@ -234,17 +240,28 @@ struct SignedPromiseBuilder {
   }
 
   bool check_signature(td::Slice signature, const td::Ed25519::PublicKey& pk) {
-    return pk.verify_signature(promise.serialize()->get_hash().as_slice(), signature).is_ok();
+    auto promise_cell = promise.serialize();
+    if (promise_cell.is_null()) {
+      return false;
+    }
+    return pk.verify_signature(promise_cell->get_hash().as_slice(), signature).is_ok();
   }
   td::SecureString calc_signature() {
-    CHECK(key);
-    return SignedPromise::signature(key, promise.serialize());
+    auto promise_cell = promise.serialize();
+    if (!key || promise_cell.is_null()) {
+      return {};
+    }
+    return SignedPromise::signature(key, promise_cell);
   }
   td::Ref<vm::Cell> finalize() {
+    auto promise_cell = promise.serialize();
+    if (promise_cell.is_null()) {
+      return {};
+    }
     if (o_signature) {
-      return SignedPromise::create_and_serialize(o_signature.value().copy(), promise.serialize());
+      return SignedPromise::create_and_serialize(o_signature.value().copy(), std::move(promise_cell));
     } else {
-      return SignedPromise::create_and_serialize(key, promise.serialize());
+      return SignedPromise::create_and_serialize(key, std::move(promise_cell));
     }
   }
 };
```

### crypto/smc-envelope/SmartContract.cpp
```diff
@@ -16,6 +16,8 @@
 
     Copyright 2017-2020 Telegram Systems LLP
 */
+#include <exception>
+
 #include "block/block-auto.h"
 #include "block/block.h"
 #include "td/utils/crypto.h"
@@ -38,6 +40,23 @@ unsigned SmartContract::Answer::output_actions_count(td::Ref<vm::Cell> list) {
   return static_cast<unsigned>(i);
 }
 namespace {
+constexpr td::uint32 max_smc_library_loads = 8;
+
+SmartContract::Answer make_error_answer(const SmartContract::State& state, td::int32 code, td::Slice message) {
+  SmartContract::Answer res;
+  res.new_state = state;
+  res.accepted = false;
+  res.success = false;
+  res.stack = td::Ref<vm::Stack>(true);
+  res.actions = {};
+  res.code = code;
+  res.gas_used = 0;
+  res.vm_log = message.str();
+  if (!res.vm_log.empty() && res.vm_log.back() != '\n') {
+    res.vm_log.push_back('\n');
+  }
+  return res;
+}
 
 td::Ref<vm::Cell> build_internal_message(td::RefInt256 amount, td::Ref<vm::CellSlice> body, SmartContract::Args args) {
   vm::CellBuilder cb;
@@ -269,23 +288,47 @@ SmartContract::Answer run_smartcont(SmartContract::State state, td::Ref<vm::Stac
   if (!libraries.is_null()) {
     vm.register_library_collection(libraries);
   }
+  td::uint32 max_library_loads = max_smc_library_loads;
   if (config) {
     auto r_limits = config->get_size_limits_config();
     if (r_limits.is_ok()) {
       vm.set_max_data_depth(r_limits.ok().max_vm_data_depth);
+      if (r_limits.ok().max_transaction_library_loads &&
+          r_limits.ok().max_transaction_library_loads.value() < max_library_loads) {
+        max_library_loads = r_limits.ok().max_transaction_library_loads.value();
+      }
     }
   }
+  vm.set_max_library_loads(max_library_loads);
+  bool unhandled_exception = false;
+  auto set_unhandled_exception = [&](int exit_code, const char* message) {
+    unhandled_exception = true;
+    res.code = ~exit_code;
+    logger.res.append("Unhandled VM exception: ");
+    logger.res.append(message ? message : "unknown exception");
+    logger.res.push_back('\n');
+  };
   try {
     res.code = ~vm.run();
+  } catch (const vm::VmError& err) {
+    set_unhandled_exception(err.get_errno(), err.get_msg());
+  } catch (const vm::VmVirtError& err) {
+    set_unhandled_exception(err.get_errno(), err.get_msg());
+  } catch (const vm::VmNoGas& err) {
+    set_unhandled_exception(err.get_errno(), err.get_msg());
+  } catch (const vm::VmFatal&) {
+    set_unhandled_exception(static_cast<int>(vm::Excno::fatal), "fatal error");
+  } catch (const std::exception& err) {
+    set_unhandled_exception(static_cast<int>(vm::Excno::fatal), err.what());
   } catch (...) {
-    LOG(FATAL) << "catch unhandled exception";
+    set_unhandled_exception(static_cast<int>(vm::Excno::fatal), "unknown exception");
   }
   res.new_state = std::move(state);
   res.stack = vm.get_stack_ref();
   gas = vm.get_gas_limits();
   res.gas_used = gas.gas_consumed();
   res.accepted = gas.gas_credit == 0;
-  res.success = (res.accepted && vm.committed());
+  res.success = (!unhandled_exception && res.accepted && vm.committed());
   res.vm_log = logger.res;
   if (GET_VERBOSITY_LEVEL() >= VERBOSITY_NAME(DEBUG)) {
     LOG(DEBUG) << "VM log\n" << logger.res;
@@ -334,10 +377,18 @@ td::Ref<vm::CellSlice> SmartContract::empty_slice() {
 }
 
 size_t SmartContract::code_size() const {
-  return vm::std_boc_serialize(state_.code).ok().size();
+  auto r_data = vm::std_boc_serialize(state_.code);
+  if (r_data.is_error()) {
+    return 0;
+  }
+  return r_data.ok().size();
 }
 size_t SmartContract::data_size() const {
-  return vm::std_boc_serialize(state_.data).ok().size();
+  auto r_data = vm::std_boc_serialize(state_.data);
+  if (r_data.is_error()) {
+    return 0;
+  }
+  return r_data.ok().size();
 }
 
 block::StdAddress SmartContract::get_address(WorkchainId workchain_id) const {
@@ -356,13 +407,21 @@ SmartContract::Answer SmartContract::run_method(Args args) {
     args.c7 = prepare_vm_c7(args, state_.code);
   }
   if (!args.limits) {
-    bool is_internal = args.get_method_id().ok() == 0;
+    auto r_method_id = args.get_method_id();
+    if (r_method_id.is_error()) {
+      return make_error_answer(get_state(), ~static_cast<td::int32>(vm::Excno::fatal), r_method_id.error().message());
+    }
+    bool is_internal = r_method_id.ok() == 0;
 
     args.limits = vm::GasLimits{is_internal ? (long long)args.amount * 1000 : (long long)0, (long long)1000000,
                                 is_internal ? 0 : (long long)10000};
   }
-  CHECK(args.stack);
-  CHECK(args.method_id);
+  if (!args.stack) {
+    return make_error_answer(get_state(), ~static_cast<td::int32>(vm::Excno::fatal), "Args has no stack");
+  }
+  if (!args.method_id) {
+    return make_error_answer(get_state(), ~static_cast<td::int32>(vm::Excno::fatal), "Args has no method id");
+  }
   args.stack.value().write().push_smallint(args.method_id.unwrap());
   auto res =
       run_smartcont(get_state(), args.stack.unwrap(), args.c7.unwrap(), args.limits.unwrap(), args.ignore_chksig,
@@ -385,7 +444,9 @@ SmartContract::Answer SmartContract::run_get_method(Args args) const {
   if (!args.stack) {
     args.stack = td::Ref<vm::Stack>(true);
   }
-  CHECK(args.method_id);
+  if (!args.method_id) {
+    return make_error_answer(get_state(), ~static_cast<td::int32>(vm::Excno::fatal), "Args has no method id");
+  }
   args.stack.value().write().push_smallint(args.method_id.unwrap());
   return run_smartcont(get_state(), args.stack.unwrap(), args.c7.unwrap(), args.limits.unwrap(), args.ignore_chksig,
                        args.libraries ? args.libraries.unwrap().get_root_cell() : td::Ref<vm::Cell>{},
```

### crypto/smc-envelope/SmartContractCode.cpp
```diff
@@ -157,11 +157,14 @@ td::Span<int> SmartContractCode::get_revisions(Type type) {
       return res;
     }
   }
-  UNREACHABLE();
+  return {};
 }
 
 td::Result<int> SmartContractCode::validate_revision(Type type, int revision) {
   auto revisions = get_revisions(type);
+  if (revisions.empty()) {
+    return td::Status::Error("Unknown smart contract code type");
+  }
   if (revision == -1) {
     if (revisions[0] == -1) {
       return -1;
@@ -180,7 +183,11 @@ td::Result<int> SmartContractCode::validate_revision(Type type, int revision) {
 }
 
 td::Ref<vm::Cell> SmartContractCode::get_code(Type type, int ext_revision) {
-  auto revision = validate_revision(type, ext_revision).move_as_ok();
+  auto r_revision = validate_revision(type, ext_revision);
+  if (r_revision.is_error()) {
+    return {};
+  }
+  auto revision = r_revision.move_as_ok();
   auto basename = [](Type type) -> td::Slice {
     switch (type) {
       case Type::WalletV3:
@@ -200,12 +207,23 @@ td::Ref<vm::Cell> SmartContractCode::get_code(Type type, int ext_revision) {
       case Type::WalletV4:
         return "wallet-v4";
     }
-    UNREACHABLE();
+    return {};
   }(type);
+  if (basename.empty()) {
+    return {};
+  }
   if (revision == -1) {
-    return load(basename).move_as_ok();
+    auto r_code = load(basename);
+    if (r_code.is_error()) {
+      return {};
+    }
+    return r_code.move_as_ok();
+  }
+  auto r_code = load(PSLICE() << basename << "-r" << revision);
+  if (r_code.is_error()) {
+    return {};
   }
-  return load(PSLICE() << basename << "-r" << revision).move_as_ok();
+  return r_code.move_as_ok();
 }
 
 }  // namespace ton
```

### crypto/smc-envelope/TestGiver.cpp
```diff
@@ -36,14 +36,20 @@ vm::CellHash TestGiver::get_init_code_hash() noexcept {
 }
 
 td::Ref<vm::Cell> TestGiver::make_a_gift_message_static(td::uint32 seqno, td::Span<Gift> gifts) noexcept {
-  CHECK(gifts.size() <= max_gifts_size);
+  if (gifts.size() > max_gifts_size) {
+    return {};
+  }
 
   vm::CellBuilder cb;
   cb.store_long(seqno, 32);
 
   for (auto& gift : gifts) {
     td::int32 send_mode = 1;
-    cb.store_long(send_mode, 8).store_ref(create_int_message(gift));
+    auto message = create_int_message(gift);
+    if (message.is_null()) {
+      return {};
+    }
+    cb.store_long(send_mode, 8).store_ref(std::move(message));
   }
 
   return cb.finalize();
```
