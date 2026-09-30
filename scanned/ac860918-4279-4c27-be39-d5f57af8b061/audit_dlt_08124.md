# [?] multisig: fix critical vulnerabilities in signing

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-12-06
Source: https://github.com/monero-project/monero/commit/c7b2944f8960c208ceddeb3075a673630ae000cd
Type: security-commit

## Details
multisig: fix critical vulnerabilities in signing

## Patch
### src/cryptonote_config.h
```diff
@@ -239,6 +239,7 @@ namespace config
   const unsigned char HASH_KEY_MEMORY = 'k';
   const unsigned char HASH_KEY_MULTISIG[] = {'M', 'u', 'l', 't' , 'i', 's', 'i', 'g', 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
   const unsigned char HASH_KEY_MULTISIG_KEY_AGGREGATION[] = "Multisig_key_agg";
+  const unsigned char HASH_KEY_CLSAG_ROUND_MULTISIG[] = "CLSAG_round_ms_merge_factor";
   const unsigned char HASH_KEY_TXPROOF_V2[] = "TXPROOF_V2";
   const unsigned char HASH_KEY_CLSAG_ROUND[] = "CLSAG_round";
   const unsigned char HASH_KEY_CLSAG_AGG_0[] = "CLSAG_agg_0";
```

### src/cryptonote_core/CMakeLists.txt
```diff
@@ -49,7 +49,6 @@ target_link_libraries(cryptonote_core
     common
     cncrypto
     blockchain_db
-    multisig
     ringct
     device
     hardforks
```

### src/cryptonote_core/cryptonote_tx_utils.cpp
```diff
@@ -203,7 +203,7 @@ namespace cryptonote
     return addr.m_view_public_key;
   }
   //---------------------------------------------------------------
-  bool construct_tx_with_tx_key(const account_keys& sender_account_keys, const std::unordered_map<crypto::public_key, subaddress_index>& subaddresses, std::vector<tx_source_entry>& sources, std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time, const crypto::secret_key &tx_key, const std::vector<crypto::secret_key> &additional_tx_keys, bool rct, const rct::RCTConfig &rct_config, rct::multisig_out *msout, bool shuffle_outs, bool use_view_tags)
+  bool construct_tx_with_tx_key(const account_keys& sender_account_keys, const std::unordered_map<crypto::public_key, subaddress_index>& subaddresses, std::vector<tx_source_entry>& sources, std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time, const crypto::secret_key &tx_key, const std::vector<crypto::secret_key> &additional_tx_keys, bool rct, const rct::RCTConfig &rct_config, bool shuffle_outs, bool use_view_tags)
   {
     hw::device &hwdev = sender_account_keys.get_device();
 
@@ -216,10 +216,6 @@ namespace cryptonote
     std::vector<rct::key> amount_keys;
     tx.set_null();
     amount_keys.clear();
-    if (msout)
-    {
-      msout->c.clear();
-    }
 
     tx.version = rct ? 2 : 1;
     tx.unlock_time = unlock_time;
@@ -333,8 +329,8 @@ namespace cryptonote
         return false;
       }
 
-      //check that derivated key is equal with real output key (if non multisig)
-      if(!msout && !(in_ephemeral.pub == src_entr.outputs[src_entr.real_output].second.dest) )
+      //check that derivated key is equal with real output key
+      if(!(in_ephemeral.pub == src_entr.outputs[src_entr.real_output].second.dest) )
       {
         LOG_ERROR("derived public key mismatch with output public key at index " << idx << ", real out " << src_entr.real_output << "! "<< ENDL << "derived_key:"
           << string_tools::pod_to_hex(in_ephemeral.pub) << ENDL << "real output_public_key:"
@@ -347,7 +343,7 @@ namespace cryptonote
       //put key image into tx input
       txin_to_key input_to_key;
       input_to_key.amount = src_entr.amount;
-      input_to_key.k_image = msout ? rct::rct2ki(src_entr.multisig_kLRki.ki) : img;
+      input_to_key.k_image = img;
 
       //fill outputs array and use relative offsets
       for(const tx_source_entry::output_entry& out_entry: src_entr.outputs)
@@ -529,7 +525,6 @@ namespace cryptonote
       rct::keyV destinations;
       std::vector<uint64_t> inamounts, outamounts;
       std::vector<unsigned int> index;
-      std::vector<rct::multisig_kLRki> kLRki;
       for (size_t i = 0; i < sources.size(); ++i)
       {
         rct::ctkey ctkey;
@@ -543,10 +538,6 @@ namespace cryptonote
         memwipe(&ctkey, sizeof(rct::ctkey));
         // inPk: (public key, commitment)
         // will be done when filling in mixRing
-        if (msout)
-        {
-          kLRki.push_back(sources[i].multisig_kLRki);
-        }
       }
       for (size_t i = 0; i < tx.vout.size(); ++i)
       {
@@ -598,9 +589,9 @@ namespace cryptonote
       get_transaction_prefix_hash(tx, tx_prefix_hash, hwdev);
       rct::ctkeyV outSk;
       if (use_simple_rct)
-        tx.rct_signatures = rct::genRctSimple(rct::hash2rct(tx_prefix_hash), inSk, destinations, inamounts, outamounts, amount_in - amount_out, mixRing, amount_keys, msout ? &kLRki : NULL, msout, index, outSk, rct_config, hwdev);
+        tx.rct_signatures = rct::genRctSimple(rct::hash2rct(tx_prefix_hash), inSk, destinations, inamounts, outamounts, amount_in - amount_out, mixRing, amount_keys, index, outSk, rct_config, hwdev);
       else
-        tx.rct_signatures = rct::genRct(rct::hash2rct(tx_prefix_hash), inSk, destinations, outamounts, mixRing, amount_keys, msout ? &kLRki[0] : NULL, msout, sources[0].real_output, outSk, rct_config, hwdev); // same index assumption
+        tx.rct_signatures = rct::genRct(rct::hash2rct(tx_prefix_hash), inSk, destinations, outamounts, mixRing, amount_keys, sources[0].real_output, outSk, rct_config, hwdev); // same index assumption
       memwipe(inSk.data(), inSk.size() * sizeof(rct::ctkey));
 
       CHECK_AND_ASSERT_MES(tx.vout.size() == outSk.size(), false, "outSk size does not match vout");
@@ -613,7 +604,7 @@ namespace cryptonote
     return true;
   }
   //---------------------------------------------------------------
-  bool construct_tx_and_get_tx_key(const account_keys& sender_account_keys, const std::unordered_map<crypto::public_key, subaddress_index>& subaddresses, std::vector<tx_source_entry>& sources, std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time, crypto::secret_key &tx_key, std::vector<crypto::secret_key> &additional_tx_keys, bool rct, const rct::RCTConfig &rct_config, rct::multisig_out *msout, bool use_view_tags)
+  bool construct_tx_and_get_tx_key(const account_keys& sender_account_keys, const std::unordered_map<crypto::public_key, subaddress_index>& subaddresses, std::vector<tx_source_entry>& sources, std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time, crypto::secret_key &tx_key, std::vector<crypto::secret_key> &additional_tx_keys, bool rct, const rct::RCTConfig &rct_config, bool use_view_tags)
   {
     hw::device &hwdev = sender_account_keys.get_device();
     hwdev.open_tx(tx_key);
@@ -634,7 +625,7 @@ namespace cryptonote
       }
 
       bool shuffle_outs = true;
-      bool r = construct_tx_with_tx_key(sender_account_keys, subaddresses, sources, destinations, change_addr, extra, tx, unlock_time, tx_key, additional_tx_keys, rct, rct_config, msout, shuffle_outs, use_view_tags);
+      bool r = construct_tx_with_tx_key(sender_account_keys, subaddresses, sources, destinations, change_addr, extra, tx, unlock_time, tx_key, additional_tx_keys, rct, rct_config, shuffle_outs, use_view_tags);
       hwdev.close_tx();
       return r;
     } catch(...) {
@@ -650,7 +641,7 @@ namespace cryptonote
      crypto::secret_key tx_key;
      std::vector<crypto::secret_key> additional_tx_keys;
      std::vector<tx_destination_entry> destinations_copy = destinations;
-     return construct_tx_and_get_tx_key(sender_account_keys, subaddresses, sources, destinations_copy, change_addr, extra, tx, unlock_time, tx_key, additional_tx_keys, false, { rct::RangeProofBorromean, 0}, NULL, false);
+     return construct_tx_and_get_tx_key(sender_account_keys, subaddresses, sources, destinations_copy, change_addr, extra, tx, unlock_time, tx_key, additional_tx_keys, false, { rct::RangeProofBorromean, 0});
   }
   //---------------------------------------------------------------
   bool generate_genesis_block(
```

### src/cryptonote_core/cryptonote_tx_utils.h
```diff
@@ -119,8 +119,8 @@ namespace cryptonote
   //---------------------------------------------------------------
   crypto::public_key get_destination_view_key_pub(const std::vector<tx_destination_entry> &destinations, const boost::optional<cryptonote::account_public_address>& change_addr);
   bool construct_tx(const account_keys& sender_account_keys, std::vector<tx_source_entry> &sources, const std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time);
-  bool construct_tx_with_tx_key(const account_keys& sender_account_keys, const std::unordered_map<crypto::public_key, subaddress_index>& subaddresses, std::vector<tx_source_entry>& sources, std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time, const crypto::secret_key &tx_key, const std::vector<crypto::secret_key> &additional_tx_keys, bool rct = false, const rct::RCTConfig &rct_config = { rct::RangeProofBorromean, 0 }, rct::multisig_out *msout = NULL, bool shuffle_outs = true, bool use_view_tags = false);
-  bool construct_tx_and_get_tx_key(const account_keys& sender_account_keys, const std::unordered_map<crypto::public_key, subaddress_index>& subaddresses, std::vector<tx_source_entry>& sources, std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time, crypto::secret_key &tx_key, std::vector<crypto::secret_key> &additional_tx_keys, bool rct = false, const rct::RCTConfig &rct_config = { rct::RangeProofBorromean, 0 }, rct::multisig_out *msout = NULL, bool use_view_tags = false);
+  bool construct_tx_with_tx_key(const account_keys& sender_account_keys, const std::unordered_map<crypto::public_key, subaddress_index>& subaddresses, std::vector<tx_source_entry>& sources, std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time, const crypto::secret_key &tx_key, const std::vector<crypto::secret_key> &additional_tx_keys, bool rct = false, const rct::RCTConfig &rct_config = { rct::RangeProofBorromean, 0 }, bool shuffle_outs = true, bool use_view_tags = false);
+  bool construct_tx_and_get_tx_key(const account_keys& sender_account_keys, const std::unordered_map<crypto::public_key, subaddress_index>& subaddresses, std::vector<tx_source_entry>& sources, std::vector<tx_destination_entry>& destinations, const boost::optional<cryptonote::account_public_address>& change_addr, const std::vector<uint8_t> &extra, transaction& tx, uint64_t unlock_time, crypto::secret_key &tx_key, std::vector<crypto::secret_key> &additional_tx_keys, bool rct = false, const rct::RCTConfig &rct_config = { rct::RangeProofBorromean, 0 }, bool use_view_tags = false);
   bool generate_output_ephemeral_keys(const size_t tx_version, const cryptonote::account_keys &sender_account_keys, const crypto::public_key &txkey_pub,  const crypto::secret_key &tx_key,
                                       const cryptonote::tx_destination_entry &dst_entr, const boost::optional<cryptonote::account_public_address> &change_addr, const size_t output_index,
                                       const bool &need_additional_txkeys, const std::vector<crypto::secret_key> &additional_tx_keys,
```

### src/multisig/CMakeLists.txt
```diff
@@ -30,7 +30,9 @@ set(multisig_sources
   multisig.cpp
   multisig_account.cpp
   multisig_account_kex_impl.cpp
-  multisig_kex_msg.cpp)
+  multisig_clsag_context.cpp
+  multisig_kex_msg.cpp
+  multisig_tx_builder_ringct.cpp)
 
 set(multisig_headers)
 
@@ -48,6 +50,7 @@ target_link_libraries(multisig
   PUBLIC
     ringct
     cryptonote_basic
+    cryptonote_core
     common
     cncrypto
   PRIVATE
```

### src/multisig/multisig_clsag_context.cpp
```diff
@@ -0,0 +1,257 @@
+// Copyright (c) 2021, The Monero Project
+// 
+// All rights reserved.
+// 
+// Redistribution and use in source and binary forms, with or without modification, are
+// permitted provided that the following conditions are met:
+// 
+// 1. Redistributions of source code must retain the above copyright notice, this list of
+//    conditions and the following disclaimer.
+// 
+// 2. Redistributions in binary form must reproduce the above copyright notice, this list
+//    of conditions and the following disclaimer in the documentation and/or other
+//    materials provided with the distribution.
+// 
+// 3. Neither the name of the copyright holder nor the names of its contributors may be
+//    used to endorse or promote products derived from this software without specific
+//    prior written permission.
+// 
+// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
+// EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
+// MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
+// THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
+// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
+// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
+// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
+// STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
+// THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
+
+#include "multisig_clsag_context.h"
+
+#include "int-util.h"
+
+#include "crypto/crypto.h"
+#include "cryptonote_config.h"
+#include "ringct/rctOps.h"
+#include "ringct/rctTypes.h"
+
+#include <cstring>
+#include <string>
+#include <vector>
+
+#undef MONERO_DEFAULT_LOG_CATEGORY
+#define MONERO_DEFAULT_LOG_CATEGORY "multisig"
+
+namespace multisig {
+
+namespace signing {
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+template<std::size_t N>
+static rct::key string_to_key(const unsigned char (&str)[N]) {
+  rct::key tmp{};
+  static_assert(sizeof(tmp.bytes) >= N, "");
+  std::memcpy(tmp.bytes, str, N);
+  return tmp;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static void encode_int_to_key_le(const unsigned int i, rct::key &k_out)
+{
+  static_assert(sizeof(unsigned int) <= sizeof(std::uint64_t), "unsigned int max too large");
+  static_assert(sizeof(std::uint64_t) <= sizeof(rct::key), "");
+  std::uint64_t temp_i{SWAP64LE(i)};
+  std::memcpy(k_out.bytes, &temp_i, sizeof(temp_i));
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+bool CLSAG_context_t::init(
+  const rct::keyV& P,
+  const rct::keyV& C_nonzero,
+  const rct::key& C_offset,
+  const rct::key& message,
+  const rct::key& I,
+  const rct::key& D,
+  const unsigned int l,
+  const rct::keyV& s,
+  const std::size_t num_alpha_components
+)
+{
+  initialized = false;
+
+  n = P.size();
+  if (n <= 0)
+    return false;
+  if (C_nonzero.size() != n)
+    return false;
+  if (s.size() != n)
+    return false;
+  if (l >= n)
+    return false;
+
+  c_params.clear();
+  c_params.reserve(n * 2 + 5);
+  b_params.clear();
+  b_params.reserve(n * 3 + 2 * num_alpha_components + 7);
+
+  c_params.push_back(string_to_key(config::HASH_KEY_CLSAG_ROUND));
+  b_params.push_back(string_to_key(config::HASH_KEY_CLSAG_ROUND_MULTISIG));
+  c_params.insert(c_params.end(), P.begin(), P.end());
+  b_params.insert(b_params.end(), P.begin(), P.end());
+  c_params.insert(c_params.end(), C_nonzero.begin(), C_nonzero.end());
+  b_params.insert(b_params.end(), C_nonzero.begin(), C_nonzero.end());
+  c_params.emplace_back(C_offset);
+  b_params.emplace_back(C_offset);
+  c_params.emplace_back(message);
+  b_params.emplace_back(message);
+  c_params_L_offset = c_params.size();
+  b_params_L_offset = b_params.size();
+  c_params.resize(c_params.size() + 1);  //this is where L will be inserted later
+  b_params.resize(b_params.size() + num_alpha_components);  //multisig aggregate public nonces for L will be inserted here later
+  c_params_R_offset = c_params.size();
+  b_params_R_offset = b_params.size();
+  c_params.resize(c_params.size() + 1);  //this is where R will be inserted later
+  b_params.resize(b_params.size() + num_alpha_components);  //multisig aggregate public nonces for R will be inserted here later
+  b_params.emplace_back(I);
+  b_params.emplace_back(D);
+  b_params.insert(b_params.end(), s.begin(), s.begin() + l);    //fake responses before 'l'
+  b_params.insert(b_params.end(), s.begin() + l + 1, s.end());  //fake responses after 'l'
+  b_params.emplace_back();
+  encode_int_to_key_le(l, b_params.back());  //real signing index 'l'
+  b_params.emplace_back();
+  encode_int_to_key_le(num_alpha_components, b_params.back());  //number of parallel nonces
+  b_params.emplace_back();
+  encode_int_to_key_le(n, b_params.back());  //number of ring members
+
+  rct::keyV mu_P_params;
+  rct::keyV mu_C_params;
+  mu_P_params.reserve(n * 2 + 4);
+  mu_C_params.reserve(n * 2 + 4);
+
+  mu_P_params.push_back(string_to_key(config::HASH_KEY_CLSAG_AGG_0));
+  mu_C_params.push_back(string_to_key(config::HASH_KEY_CLSAG_AGG_1));
+  mu_P_params.insert(mu_P_params.end(), P.begin(), P.end());
+  mu_C_params.insert(mu_C_params.end(), P.begin(), P.end());
+  mu_P_params.insert(mu_P_params.end(), C_nonzero.begin(), C_nonzero.end());
+  mu_C_params.insert(mu_C_params.end(), C_nonzero.begin(), C_nonzero.end());
+  mu_P_params.emplace_back(I);
+  mu_C_params.emplace_back(I);
+  mu_P_params.emplace_back(scalarmultKey(D, rct::INV_EIGHT));
+  mu_C_params.emplace_back(mu_P_params.back());
+  mu_P_params.emplace_back(C_offset);
+  mu_C_params.emplace_back(C_offset);
+  mu_P = hash_to_scalar(mu_P_params);
+  mu_C = hash_to_scalar(mu_C_params);
+
+  rct::geDsmp I_precomp;
+  rct::geDsmp D_precomp;
+  rct::precomp(I_precomp.k, I);
+  rct::precomp(D_precomp.k, D);
+  rct::key wH_l;
+  rct::addKeys3(wH_l, mu_P, I_precomp.k, mu_C, D_precomp.k);
+  rct::precomp(wH_l_precomp.k, wH_l);
+  W_precomp.resize(n);
+  H_precomp.resize(n);
+  for (std::size_t i = 0; i < n; ++i) {
+    rct::geDsmp P_precomp;
+    rct::geDsmp C_precomp;
+    rct::key C;
+    rct::subKeys(C, C_nonzero[i], C_offset);
+    rct::precomp(P_precomp.k, P[i]);
+    rct::precomp(C_precomp.k, C);
+    rct::key W;
+    rct::addKeys3(W, mu_P, P_precomp.k, mu_C, C_precomp.k);
+    rct::precomp(W_precomp[i].k, W);
+    ge_p3 Hi_p3;
+    rct::hash_to_p3(Hi_p3, P[i]);
+    ge_dsm_precomp(H_precomp[i].k, &Hi_p3);
+  }
+  rct::precomp(G_precomp.k, rct::G);
+  this->l = l;
+  this->s = s;
+  this->num_alpha_components = num_alpha_components;
+
+  initialized = true;
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+bool CLSAG_context_t::combine_alpha_and_compute_challenge(
+  const rct::keyV& total_alpha_G,
+  const rct::keyV& total_alpha_H,
+  const rct::keyV& alpha,
+  rct::key& alpha_combined,
+  rct::key& c_0,
+  rct::key& c
+)
+{
+  if (not initialized)
+    return false;
+
+  if (num_alpha_components != total_alpha_G.size())
+    return false;
+  if (num_alpha_components != total_alpha_H.size())
+    return false;
+  if (num_alpha_components != alpha.size())
+    return false;
+
+  // insert aggregate public nonces for L and R components
+  for (std::size_t i = 0; i < num_alpha_components; ++i) {
+    b_params[b_params_L_offset + i] = total_alpha_G[i];
+    b_params[b_params_R_offset + i] = total_alpha_H[i];
+  }
+
+  // musig2-style combination factor 'b'
+  const rct::key b = rct::hash_to_scalar(b_params);
+
+  // 1) store combined public nonces in the 'L' and 'R' slots for computing the initial challenge
+  //    - L = sum_i(b^i total_alpha_G[i])
+  //    - R = sum_i(b^i total_alpha_H[i])
+  // 2) compute the local signer's combined private nonce
+  //    - alpha_combined = sum_i(b^i * alpha[i])
+  rct::key& L_l = c_params[c_params_L_offset];
+  rct::key& R_l = c_params[c_params_R_offset];
+  rct::key b_i = rct::identity();
+  L_l = rct::identity();
+  R_l = rct::identity();
+  alpha_combined = rct::zero();
+  for (std::size_t i = 0; i < num_alpha_components; ++i) {
+    rct::addKeys(L_l, L_l, rct::scalarmultKey(total_alpha_G[i], b_i));
+    rct::addKeys(R_l, R_l, rct::scalarmultKey(total_alpha_H[i], b_i));
+    sc_muladd(alpha_combined.bytes, alpha[i].bytes, b_i.bytes, alpha_combined.bytes);
+    sc_mul(b_i.bytes, b_i.bytes, b.bytes);
+  }
+
+  // compute initial challenge from real spend components
+  c = rct::hash_to_scalar(c_params);
+
+  // 1) c_0: find the CLSAG's challenge for index '0', which will be stored in the proof
+  // note: in the CLSAG implementation in ringct/rctSigs, c_0 is denoted 'c1' (a notation error)
+  // 2) c:   find the final challenge for the multisig signers to respond to
+  for (std::size_t i = (l + 1) % n; i != l; i = (i + 1) % n) {
+    if (i == 0)
+      c_0 = c;
+    rct::addKeys3(c_params[c_params_L_offset], s[i], G_precomp.k, c, W_precomp[i].k);
+    rct::addKeys3(c_params[c_params_R_offset], s[i], H_precomp[i].k, c, wH_l_precomp.k);
+    c = rct::hash_to_scalar(c_params);
+  }
+  if (l == 0)
+    c_0 = c;
+
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+bool CLSAG_context_t::get_mu(
+  rct::key& mu_P,
+  rct::key& mu_C
+) const
+{
+  if (not initialized)
+    return false;
+  mu_P = this->mu_P;
+  mu_C = this->mu_C;
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+} //namespace signing
+
+} //namespace multisig
```

### src/multisig/multisig_clsag_context.h
```diff
@@ -0,0 +1,137 @@
+// Copyright (c) 2021, The Monero Project
+// 
+// All rights reserved.
+// 
+// Redistribution and use in source and binary forms, with or without modification, are
+// permitted provided that the following conditions are met:
+// 
+// 1. Redistributions of source code must retain the above copyright notice, this list of
+//    conditions and the following disclaimer.
+// 
+// 2. Redistributions in binary form must reproduce the above copyright notice, this list
+//    of conditions and the following disclaimer in the documentation and/or other
+//    materials provided with the distribution.
+// 
+// 3. Neither the name of the copyright holder nor the names of its contributors may be
+//    used to endorse or promote products derived from this software without specific
+//    prior written permission.
+// 
+// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
+// EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
+// MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
+// THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
+// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
+// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
+// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
+// STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
+// THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
+
+////
+// References
+// - CLSAG (base signature scheme): https://eprint.iacr.org/2019/654
+// - MuSig2 (style for multisig signing): https://eprint.iacr.org/2020/1261
+///
+
+
+#pragma once
+
+#include "ringct/rctTypes.h"
+
+#include <vector>
+
+
+namespace multisig {
+
+namespace signing {
+
+class CLSAG_context_t final {
+private:
+  // is the CLSAG context initialized?
+  bool initialized;
+  // challenge components: c = H(domain-separator, {P}, {C}, C_offset, message, L, R)
+  rct::keyV c_params;
+  // indices in c_params where L and R will be
+  std::size_t c_params_L_offset;
+  std::size_t c_params_R_offset;
+  // musig2-style nonce combination factor components for multisig signing
+  //   b = H(domain-separator, {P}, {C}, C_offset, message, {L_combined_alphas}, {R_combined_alphas}, I, D, {s_non_l}, l, k, n)
+  //   - {P} = ring of one-time addresses
+  //   - {C} = ring of amount commitments (1:1 with one-time addresses)
+  //   - C_offset = pseudo-output commitment to offset all amount commitments with
+  //   - message = message the CLSAG will sign
+  //   - {L_combined_alphas} = set of summed-together public nonces from all multisig signers for this CLSAG's L component
+  //   - {R_combined_alphas} = set of summed-together public nonces from all multisig signers for this CLSAG's R component
+  //   - I = key image for one-time address at {P}[l]
+  //   - D = auxiliary key image for the offsetted amount commitment '{C}[l] - C_offset'
+  //   - {s_non_l} = fake responses for this proof
+  //   - l = real signing index in {P} and '{C} - C_offset'
+  //   - k = number of parallel nonces that each participant provides
+  //   - n = number of ring members
+  rct::keyV b_params;
+  // indices in b_params where L and R 'alpha' components will be
+  std::size_t b_params_L_offset;
+  std::size_t b_params_R_offset;
+  // CLSAG 'concise' coefficients for {P} and '{C} - C_offset'
+  //   mu_x = H(domain-separator, {P}, {C}, I, (1/8)*D, C_offset)
+  //   - note: 'D' is stored in the form '(1/8)*D' in transaction data
+  rct::key mu_P;
+  rct::key mu_C;
+  // ring size
+  std::size_t n;
+  // aggregate key image: mu_P*I + mu_C*D
+  rct::geDsmp wH_l_precomp;
+  // aggregate ring members: mu_P*P_i + mu_C*(C_i - C_offset)
+  std::vector<rct::geDsmp> W_precomp;
+  // key image component base keys: H_p(P_i)
+  std::vector<rct::geDsmp> H_precomp;
+  // cache for later: generator 'G' in 'precomp' representation
+  rct::geDsmp G_precomp;
+  // real signing index in this CLSAG
+  std::size_t l;
+  // signature responses
+  rct::keyV s;
+  // number of signing nonces expected per signer
+  std::size_t num_alpha_components;
+public:
+  CLSAG_context_t() : initialized{false} {}
+
+  // prepare CLSAG challenge context
+  bool init(
+    const rct::keyV& P,
+    const rct::keyV& C_nonzero,
+    const rct::key& C_offset,
+    const rct::key& message,
+    const rct::key& I,
+    const rct::key& D,
+    const unsigned int l,
+    const rct::keyV& s,
+    const std::size_t num_alpha_components
+  );
+
+  // get the local signer's combined musig2-style private nonce and compute the CLSAG challenge
+  bool combine_alpha_and_compute_challenge(
+    // set of summed-together musig2-style public nonces from all multisig signers for this CLSAG's L component
+    const rct::keyV& total_alpha_G,
+    // set of summed-together musig2-style public nonces from all multisig signers for this CLSAG's R component
+    const rct::keyV& total_alpha_H,
+    // local signer's private musig2-style nonces
+    const rct::keyV& alpha,
+    // local signer's final private nonce, using musig2-style combination with factor 'b'
+    //    alpha_combined = sum_i(b^i * alpha[i])
+    rct::key& alpha_combined,
+    // CLSAG challenge to store in the proof
+    rct::key& c_0,
+    // final CLSAG challenge to respond to (need this to make multisig partial signatures)
+    rct::key& c
+  );
+
+  // getter for CLSAG 'concise' coefficients
+  bool get_mu(
+    rct::key& mu_P,
+    rct::key& mu_C
+  ) const;
+};
+
+} //namespace signing
+
+} //namespace multisig
```

### src/multisig/multisig_tx_builder_ringct.cpp
```diff
@@ -0,0 +1,943 @@
+// Copyright (c) 2021, The Monero Project
+// 
+// All rights reserved.
+// 
+// Redistribution and use in source and binary forms, with or without modification, are
+// permitted provided that the following conditions are met:
+// 
+// 1. Redistributions of source code must retain the above copyright notice, this list of
+//    conditions and the following disclaimer.
+// 
+// 2. Redistributions in binary form must reproduce the above copyright notice, this list
+//    of conditions and the following disclaimer in the documentation and/or other
+//    materials provided with the distribution.
+// 
+// 3. Neither the name of the copyright holder nor the names of its contributors may be
+//    used to endorse or promote products derived from this software without specific
+//    prior written permission.
+// 
+// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
+// EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
+// MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
+// THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
+// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
+// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
+// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
+// STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
+// THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
+
+#include "multisig_tx_builder_ringct.h"
+
+#include "int-util.h"
+#include "memwipe.h"
+
+#include "cryptonote_basic/cryptonote_basic.h"
+#include "cryptonote_basic/account.h"
+#include "cryptonote_basic/cryptonote_format_utils.h"
+#include "cryptonote_core/cryptonote_tx_utils.h"
+#include "device/device.hpp"
+#include "multisig_clsag_context.h"
+#include "ringct/bulletproofs.h"
+#include "ringct/bulletproofs_plus.h"
+#include "ringct/rctSigs.h"
+
+#include <boost/multiprecision/cpp_int.hpp>
+
+#include <algorithm>
+#include <cstring>
+#include <limits>
+#include <set>
+#include <unordered_map>
+#include <unordered_set>
+#include <vector>
+
+#undef MONERO_DEFAULT_LOG_CATEGORY
+#define MONERO_DEFAULT_LOG_CATEGORY "multisig"
+
+namespace multisig {
+
+namespace signing {
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+bool view_tag_required(const int bp_version)
+{
+  // view tags were introduced at the same time as BP+, so they are needed after BP+ (v4 and later)
+  if (bp_version <= 3)
+    return false;
+  else
+    return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static void sort_sources(
+  std::vector<cryptonote::tx_source_entry>& sources
+)
+{
+  std::sort(sources.begin(), sources.end(), [](const auto& lhs, const auto& rhs){
+    const rct::key& ki0 = lhs.multisig_kLRki.ki;
+    const rct::key& ki1 = rhs.multisig_kLRki.ki;
+    return memcmp(&ki0, &ki1, sizeof(rct::key)) > 0;
+  });
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool compute_keys_for_sources(
+  const cryptonote::account_keys& account_keys,
+  const std::vector<cryptonote::tx_source_entry>& sources,
+  const std::uint32_t subaddr_account,
+  const std::set<std::uint32_t>& subaddr_minor_indices,
+  rct::keyV& input_secret_keys
+)
+{
+  const std::size_t num_sources = sources.size();
+  hw::device& hwdev = account_keys.get_device();
+  std::unordered_map<crypto::public_key, cryptonote::subaddress_index> subaddresses;
+  for (const std::uint32_t minor_index: subaddr_minor_indices) {
+    subaddresses[hwdev.get_subaddress_spend_public_key(
+      account_keys,
+      {subaddr_account, minor_index}
+    )] = {subaddr_account, minor_index};
+  }
+  input_secret_keys.resize(num_sources);
+  for (std::size_t i = 0; i < num_sources; ++i) {
+    const auto& src = sources[i];
+    crypto::key_image tmp_key_image;
+    cryptonote::keypair tmp_keys;
+    if (src.real_output >= src.outputs.size())
+      return false;
+    if (not cryptonote::generate_key_image_helper(
+      account_keys,
+      subaddresses,
+      rct::rct2pk(src.outputs[src.real_output].second.dest),
+      src.real_out_tx_key,
+      src.real_out_additional_tx_keys,
+      src.real_output_in_tx_index,
+      tmp_keys,
+      tmp_key_image,
+      hwdev
+    )) {
+      return false;
+    }
+    input_secret_keys[i] = rct::sk2rct(tmp_keys.sec);
+  }
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static void shuffle_destinations(
+  std::vector<cryptonote::tx_destination_entry>& destinations
+)
+{
+  std::shuffle(destinations.begin(), destinations.end(), crypto::random_device{});
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool set_tx_extra(
+  const cryptonote::account_keys& account_keys,
+  const std::vector<cryptonote::tx_destination_entry>& destinations,
+  const cryptonote::tx_destination_entry& change,
+  const crypto::secret_key& tx_secret_key,
+  const crypto::public_key& tx_public_key,
+  const std::vector<crypto::public_key>& tx_aux_public_keys,
+  const std::vector<std::uint8_t>& extra,
+  cryptonote::transaction& tx
+)
+{
+  hw::device &hwdev = account_keys.get_device();
+  tx.extra = extra;
+  // if we have a stealth payment id, find it and encrypt it with the tx key now
+  std::vector<cryptonote::tx_extra_field> tx_extra_fields;
+  if (cryptonote::parse_tx_extra(tx.extra, tx_extra_fields))
+  {
+    bool add_dummy_payment_id = true;
+    cryptonote::tx_extra_nonce extra_nonce;
+    if (cryptonote::find_tx_extra_field_by_type(tx_extra_fields, extra_nonce))
+    {
+      crypto::hash payment_id = crypto::null_hash;
+      crypto::hash8 payment_id8 = crypto::null_hash8;
+      if (cryptonote::get_encrypted_payment_id_from_tx_extra_nonce(extra_nonce.nonce, payment_id8))
+      {
+        LOG_PRINT_L2("Encrypting payment id " << payment_id8);
+        crypto::public_key view_key_pub = cryptonote::get_destination_view_key_pub(destinations, change.addr);
+        if (view_key_pub == crypto::null_pkey)
+        {
+          // valid combinations:
+          // - 1 output with encrypted payment ID, dummy change output (0 amount)
+          // - 0 outputs,                          1 change output with encrypted payment ID
+          // - 1 output with encrypted payment ID, 1 change output
+          LOG_ERROR("Destinations have to have exactly one output to support encrypted payment ids");
+          return false;
+        }
+
+        if (!hwdev.encrypt_payment_id(payment_id8, view_key_pub, tx_secret_key))
+        {
+          LOG_ERROR("Failed to encrypt payment id");
+          return false;
+        }
+
+        std::string extra_nonce_updated;
+        cryptonote::set_encrypted_payment_id_to_tx_extra_nonce(extra_nonce_updated, payment_id8);
+        cryptonote::remove_field_from_tx_extra(tx.extra, typeid(cryptonote::tx_extra_nonce));
+        if (!cryptonote::add_extra_nonce_to_tx_extra(tx.extra, extra_nonce_updated))
+        {
+          LOG_ERROR("Failed to add encrypted payment id to tx extra");
+          return false;
+        }
+        LOG_PRINT_L1("Encrypted payment ID: " << payment_id8);
+        add_dummy_payment_id = false;
+      }
+      else if (cryptonote::get_payment_id_from_tx_extra_nonce(extra_nonce.nonce, payment_id))
+      {
+        add_dummy_payment_id = false;
+      }
+    }
+
+    // we don't add one if we've got more than the usual 1 destination plus change
+    if (destinations.size() > 2)
+      add_dummy_payment_id = false;
+
+    if (add_dummy_payment_id)
+    {
+      // if we have neither long nor short payment id, add a dummy short one,
+      // this should end up being the vast majority of txes as time goes on
+      std::string extra_nonce_updated;
+      crypto::hash8 payment_id8 = crypto::null_hash8;
+      crypto::public_key view_key_pub = cryptonote::get_destination_view_key_pub(destinations, change.addr);
+      if (view_key_pub == crypto::null_pkey)
+      {
+        LOG_ERROR("Failed to get key to encrypt dummy payment id with");
+      }
+      else
+      {
+        hwdev.encrypt_payment_id(payment_id8, view_key_pub, tx_secret_key);
+        cryptonote::set_encrypted_payment_id_to_tx_extra_nonce(extra_nonce_updated, payment_id8);
+        if (!cryptonote::add_extra_nonce_to_tx_extra(tx.extra, extra_nonce_updated))
+        {
+          LOG_ERROR("Failed to add dummy encrypted payment id to tx extra");
+          // continue anyway
+        }
+      }
+    }
+  }
+  else
+  {
+    MWARNING("Failed to parse tx extra");
+    tx_extra_fields.clear();
+  }
+
+  cryptonote::remove_field_from_tx_extra(tx.extra, typeid(cryptonote::tx_extra_pub_key));
+  cryptonote::add_tx_pub_key_to_extra(tx.extra, tx_public_key);
+  cryptonote::remove_field_from_tx_extra(tx.extra, typeid(cryptonote::tx_extra_additional_pub_keys));
+  LOG_PRINT_L2("tx pubkey: " << tx_public_key);
+  if (tx_aux_public_keys.size())
+  {
+    LOG_PRINT_L2("additional tx pubkeys: ");
+    for (size_t i = 0; i < tx_aux_public_keys.size(); ++i)
+      LOG_PRINT_L2(tx_aux_public_keys[i]);
+    cryptonote::add_additional_tx_pub_keys_to_extra(tx.extra, tx_aux_public_keys);
+  }
+  if (not cryptonote::sort_tx_extra(tx.extra, tx.extra))
+    return false;
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool compute_keys_for_destinations(
+  const cryptonote::account_keys& account_keys,
+  const std::uint32_t subaddr_account,
+  const std::vector<cryptonote::tx_destination_entry>& destinations,
+  const cryptonote::tx_destination_entry& change,
+  const std::vector<std::uint8_t>& extra,
+  const bool use_view_tags,
+  const bool reconstruction,
+  crypto::secret_key& tx_secret_key,
+  std::vector<crypto::secret_key>& tx_aux_secret_keys,
+  rct::keyV& output_public_keys,
+  rct::keyV& output_amount_secret_keys,
+  std::vector<crypto::view_tag>& view_tags,
+  cryptonote::transaction& unsigned_tx
+)
+{
+  hw::device &hwdev = account_keys.get_device();
+
+  // check non-zero change amount case
+  if (change.amount > 0)
+  {
+    // the change output must be directed to the local account
+    if (change.addr != hwdev.get_subaddress(account_keys, {subaddr_account}))
+      return false;
+
+    // expect the change destination to be in the destination set
+    if (std::find_if(destinations.begin(), destinations.end(),
+        [&change](const auto &destination) -> bool
+        {
+          return destination.addr == change.addr;
+        }) == destinations.end())
+      return false;
+  }
+
+  // collect non-change recipients into normal/subaddress buckets
+  std::unordered_set<cryptonote::account_public_address> unique_subbaddr_recipients;
+  std::unordered_set<cryptonote::account_public_address> unique_std_recipients;
+  for(const auto& dst_entr: destinations) {
+    if (dst_entr.addr == change.addr)
+      continue;
+    if (dst_entr.is_subaddress)
+      unique_subbaddr_recipients.insert(dst_entr.addr);
+    else
+      unique_std_recipients.insert(dst_entr.addr);
+  }
+
+  if (not reconstruction) {
+    tx_secret_key = rct::rct2sk(rct::skGen());
+  }
+
+  // tx pub key: R
+  crypto::public_key tx_public_key;
+  if (unique_std_recipients.empty() && unique_subbaddr_recipients.size() == 1) {
+    // if there is exactly 1 non-change recipient, and it's to a subaddress, then the tx pubkey = r*Ksi_nonchange_recipient
+    tx_public_key = rct::rct2pk(
+      hwdev.scalarmultKey(
+        rct::pk2rct(unique_subbaddr_recipients.begin()->m_spend_public_key),
+        rct::sk2rct(tx_secret_key)
+    ));
+  }
+  else {
+    // otherwise, the tx pub key = r*G
+    // - if there are > 1 non-change recipients, with at least one to a subaddress, then the tx pubkey is not used
+    //   (additional tx keys will be used instead)
+    // - if all non-change recipients are to normal addresses, then the tx pubkey will be used by all recipients
+    //   (including change recipient, even if change is to a subaddress)
+    tx_public_key = rct::rct2pk(hwdev.scalarmultBase(rct::sk2rct(tx_secret_key)));
+  }
+
+  // additional tx pubkeys: R_t
+  // - add if there are > 1 non-change recipients, with at least one to a subaddress
+  const std::size_t num_destinations = destinations.size();
+
+  const bool need_tx_aux_keys = unique_subbaddr_recipients.size() + bool(unique_std_recipients.size()) > 1;
+  if (not reconstruction and need_tx_aux_keys) {
+    tx_aux_secret_keys.clear();
+    tx_aux_secret_keys.reserve(num_destinations);
+    for(std::size_t i = 0; i < num_destinations; ++i)
+      tx_aux_secret_keys.push_back(rct::rct2sk(rct::skGen()));
+  }
+
+  output_public_keys.resize(num_destinations);
+  view_tags.resize(num_destinations);
+  std::vector<crypto::public_key> tx_aux_public_keys;
+  crypto::public_key temp_output_public_key;
+
+  for (std::size_t i = 0; i < num_destinations; ++i) {
+    if (not hwdev.generate_output_ephemeral_keys(
+      unsigned_tx.version,
+      account_keys,
+      tx_public_key,
+      tx_secret_key,
+      destinations[i],
+      change.addr,
+      i,
+      need_tx_aux_keys,
+      tx_aux_secret_keys,
+      tx_aux_public_keys,
+      output_amount_secret_keys,
+      temp_output_public_key,
+      use_view_tags,
+      view_tags[i]  //unused variable if use_view_tags is not set
+    )) {
+      return false;
+    }
+    output_public_keys[i] = rct::pk2rct(temp_output_public_key);
+  }
+
+  if (num_destinations != output_amount_secret_keys.size())
+    return false;
+
+  CHECK_AND_ASSERT_MES(
+    tx_aux_public_keys.size() == tx_aux_secret_keys.size(),
+    false,
+    "Internal error creating additional public keys"
+  );
+
+  if (not set_tx_extra(account_keys, destinations, change, tx_secret_key, tx_public_key, tx_aux_public_keys, extra, unsigned_tx))
+    return false;
+
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static void set_tx_inputs(
+  const std::vector<cryptonote::tx_source_entry>& sources,
+  cryptonote::transaction& unsigned_tx
+)
+{
+  const std::size_t num_sources = sources.size();
+  unsigned_tx.vin.resize(num_sources);
+  for (std::size_t i = 0; i < num_sources; ++i) {
+    std::vector<std::uint64_t> offsets;
+    offsets.reserve(sources[i].outputs.size());
+    for (const auto& e: sources[i].outputs)
+      offsets.emplace_back(e.first);
+    unsigned_tx.vin[i] = cryptonote::txin_to_key{
+      .amount = 0,
+      .key_offsets = cryptonote::absolute_output_offsets_to_relative(offsets),
+      .k_image = rct::rct2ki(sources[i].multisig_kLRki.ki),
+    };
+  }
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool onetime_addresses_are_unique(const rct::keyV& output_public_keys)
+{
+  for (auto addr_it = output_public_keys.begin(); addr_it != output_public_keys.end(); ++addr_it)
+  {
+    if (std::find(output_public_keys.begin(), addr_it, *addr_it) != addr_it)
+      return false;
+  }
+
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool set_tx_outputs(const rct::keyV& output_public_keys, cryptonote::transaction& unsigned_tx)
+{
+  // sanity check: all onetime addresses should be unique
+  if (not onetime_addresses_are_unique(output_public_keys))
+    return false;
+
+  // set the tx outputs
+  const std::size_t num_destinations = output_public_keys.size();
+  unsigned_tx.vout.resize(num_destinations);
+  for (std::size_t i = 0; i < num_destinations; ++i)
+    cryptonote::set_tx_out(0, rct::rct2pk(output_public_keys[i]), false, crypto::view_tag{}, unsigned_tx.vout[i]);
+
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool set_tx_outputs_with_view_tags(
+  const rct::keyV& output_public_keys,
+  const std::vector<crypto::view_tag>& view_tags,
+  cryptonote::transaction& unsigned_tx
+)
+{
+  // sanity check: all onetime addresses should be unique
+  if (not onetime_addresses_are_unique(output_public_keys))
+    return false;
+
+  // set the tx outputs (with view tags)
+  const std::size_t num_destinations = output_public_keys.size();
+  CHECK_AND_ASSERT_MES(view_tags.size() == num_destinations, false,
+    "multisig signing protocol: internal error, view tag size mismatch.");
+  unsigned_tx.vout.resize(num_destinations);
+  for (std::size_t i = 0; i < num_destinations; ++i)
+    cryptonote::set_tx_out(0, rct::rct2pk(output_public_keys[i]), true, view_tags[i], unsigned_tx.vout[i]);
+
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static void make_new_range_proofs(const int bp_version,
+  const std::vector<std::uint64_t>& output_amounts,
+  const rct::keyV& output_amount_masks,
+  rct::rctSigPrunable& sigs)
+{
+  sigs.bulletproofs.clear();
+  sigs.bulletproofs_plus.clear();
+
+  if (bp_version == 3)
+    sigs.bulletproofs.push_back(rct::bulletproof_PROVE(output_amounts, output_amount_masks));
+  else if (bp_version == 4)
+    sigs.bulletproofs_plus.push_back(rct::bulletproof_plus_PROVE(output_amounts, output_amount_masks));
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool try_reconstruct_range_proofs(const int bp_version,
+  const rct::rctSigPrunable& original_sigs,
+  const std::size_t num_destinations,
+  const rct::ctkeyV& output_public_keys,
+  rct::rctSigPrunable& reconstructed_sigs)
+{
+  auto try_reconstruct_range_proofs =
+    [&](const auto &original_range_proofs, auto &new_range_proofs) -> bool
+    {
+      if (original_range_proofs.size() != 1)
+        return false;
+
+      new_range_proofs = original_range_proofs;
+      new_range_proofs[0].V.resize(num_destinations);
+      for (std::size_t i = 0; i < num_destinations; ++i)
+        new_range_proofs[0].V[i] = rct::scalarmultKey(output_public_keys[i].mask, rct::INV_EIGHT);
+
+      return true;
+    };
+
+  if (bp_version == 3)
+  {
+    if (not try_reconstruct_range_proofs(original_sigs.bulletproofs, reconstructed_sigs.bulletproofs))
+      return false;
+    return rct::bulletproof_VERIFY(reconstructed_sigs.bulletproofs);
+  }
+  else if (bp_version == 4)
+  {
+    if (not try_reconstruct_range_proofs(original_sigs.bulletproofs_plus, reconstructed_sigs.bulletproofs_plus))
+      return false;
+    return rct::bulletproof_plus_VERIFY(reconstructed_sigs.bulletproofs_plus);
+  }
+
+  return false;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool set_tx_rct_signatures(
+  const std::uint64_t fee,
+  const std::vector<cryptonote::tx_source_entry>& sources,
+  const std::vector<cryptonote::tx_destination_entry>& destinations,
+  const rct::keyV& input_secret_keys,
+  const rct::keyV& output_public_keys,
+  const rct::keyV& output_amount_secret_keys,
+  const rct::RCTConfig& rct_config,
+  const bool reconstruction,
+  cryptonote::transaction& unsigned_tx,
+  std::vector<CLSAG_context_t>& CLSAG_contexts,
+  rct::keyV& cached_w
+)
+{
+  if (rct_config.bp_version != 3 &&
+      rct_config.bp_version != 4)
+    return false;
+  if (rct_config.range_proof_type != rct::RangeProofPaddedBulletproof)
+    return false;
+
+  const std::size_t num_destinations = destinations.size();
+  const std::size_t num_sources = sources.size();
+
+  // rct_signatures component of tx
+  rct::rctSig rv{};
+
+  // set misc. fields
+  if (rct_config.bp_version == 3)
+    rv.type = rct::RCTTypeCLSAG;
+  else if (rct_config.bp_version == 4)
+    rv.type = rct::RCTTypeBulletproofPlus;
+  else
+    return false;
+  rv.txnFee = fee;
+  rv.message = rct::hash2rct(cryptonote::get_transaction_prefix_hash(unsigned_tx));
+
+  // define outputs
+  std::vector<std::uint64_t> output_amounts(num_destinations);
+  rct::keyV output_amount_masks(num_destinations);
+  rv.ecdhInfo.resize(num_destinations);
+  rv.outPk.resize(num_destinations);
+  for (std::size_t i = 0; i < num_destinations; ++i) {
+    rv.outPk[i].dest = output_public_keys[i];
+    output_amounts[i] = destinations[i].amount;
+    output_amount_masks[i] = genCommitmentMask(output_amount_secret_keys[i]);
+    rv.ecdhInfo[i].amount = rct::d2h(output_amounts[i]);
+    rct::addKeys2(
+      rv.outPk[i].mask,
+      output_amount_masks[i],
+      rv.ecdhInfo[i].amount,
+      rct::H
+    );
+    rct::ecdhEncode(rv.ecdhInfo[i], output_amount_secret_keys[i], true);
+  }
+
+  // output range proofs
+  if (not reconstruction) {
+    make_new_range_proofs(rct_config.bp_version, output_amounts, output_amount_masks, rv.p);
+  }
+  else {
+    if (not try_reconstruct_range_proofs(rct_config.bp_version,
+        unsigned_tx.rct_signatures.p,
+        num_destinations,
+        rv.outPk,
+        rv.p))
+      return false;
+  }
+
+  // prepare rings for input CLSAGs
+  rv.mixRing.resize(num_sources);
+  for (std::size_t i = 0; i < num_sources; ++i) {
+    const std::size_t ring_size = sources[i].outputs.size();
+    rv.mixRing[i].resize(ring_size);
+    for (std::size_t j = 0; j < ring_size; ++j) {
+      rv.mixRing[i][j].dest = sources[i].outputs[j].second.dest;
+      rv.mixRing[i][j].mask = sources[i].outputs[j].second.mask;
+    }
+  }
+
+  // make pseudo-output commitments
+  rct::keyV a;  //pseudo-output commitment blinding factors
+  auto a_wiper = epee::misc_utils::create_scope_leave_handler([&]{
+    memwipe(static_cast<rct::key *>(a.data()), a.size() * sizeof(rct::key));
+  });
+  if (not reconstruction) {
+    a.resize(num_sources);
+    rv.p.pseudoOuts.resize(num_sources);
+    a[num_sources - 1] = rct::zero();
+    for (std::size_t i = 0; i < num_destinations; ++i) {
+      sc_add(
+        a[num_sources - 1].bytes,
+        a[num_sources - 1].bytes,
+        output_amount_masks[i].bytes
+      );
+    }
+    for (std::size_t i = 0; i < num_sources - 1; ++i) {
+      rct::skGen(a[i]);
+      sc_sub(
+        a[num_sources - 1].bytes,
+        a[num_sources - 1].bytes,
+        a[i].bytes
+      );
+      rct::genC(rv.p.pseudoOuts[i], a[i], sources[i].amount);
+    }
+    rct::genC(
+      rv.p.pseudoOuts[num_sources - 1],
+      a[num_sources - 1],
+      sources[num_sources - 1].amount
+    );
+  }
+  // check balance if reconstructing the tx
+  else {
+    rv.p.pseudoOuts = unsigned_tx.rct_signatures.p.pseudoOuts;
+    if (num_sources != rv.p.pseudoOuts.size())
+      return false;
+    rct::key balance_accumulator = rct::scalarmultH(rct::d2h(fee));
+    for (const auto& e: rv.outPk)
+      rct::addKeys(balance_accumulator, balance_accumulator, e.mask);
+    for (const auto& pseudoOut: rv.p.pseudoOuts)
+      rct::subKeys(balance_accumulator, balance_accumulator, pseudoOut);
+    if (not (balance_accumulator == rct::identity()))
+      return false;
+  }
+
+  // prepare input CLSAGs for signing
+  const rct::key message = get_pre_mlsag_hash(rv, hw::get_device("default"));
+
+  rv.p.CLSAGs.resize(num_sources);
+  if (reconstruction) {
+    if (num_sources != unsigned_tx.rct_signatures.p.CLSAGs.size())
+      return false;
+  }
+
+  CLSAG_contexts.resize(num_sources);
+  if (not reconstruction)
+    cached_w.resize(num_sources);
+
+  for (std::size_t i = 0; i < num_sources; ++i) {
+    const std::size_t ring_size = rv.mixRing[i].size();
+    const rct::key& I = sources[i].multisig_kLRki.ki;
+    const std::size_t l = sources[i].real_output;
+    if (l >= ring_size)
+      return false;
+    rct::keyV& s = rv.p.CLSAGs[i].s;
+    const rct::key& C_offset = rv.p.pseudoOuts[i];
+    rct::keyV P(ring_size);
+    rct::keyV C_nonzero(ring_size);
+
+    if (not reconstruction) {
+      s.resize(ring_size);
+      for (std::size_t j = 0; j < ring_size; ++j) {
+        if (j != l)
+          s[j] = rct::skGen();  //make fake responses
+      }
+    }
+    else {
+      if (ring_size != unsigned_tx.rct_signatures.p.CLSAGs[i].s.size())
+        return false;
+      s = unsigned_tx.rct_signatures.p.CLSAGs[i].s;
+    }
+
+    for (std::size_t j = 0; j < ring_size; ++j) {
+      P[j] = rv.mixRing[i][j].dest;
+      C_nonzero[j] = rv.mixRing[i][j].mask;
+    }
+
+    rct::key D;
+    rct::key z;
+    auto z_wiper = epee::misc_utils::create_scope_leave_handler([&]{
+      memwipe(static_cast<rct::key *>(&z), sizeof(rct::key));
+    });
+    if (not reconstruction) {
+      sc_sub(z.bytes, sources[i].mask.bytes, a[i].bytes);  //commitment to zero privkey
+      ge_p3 H_p3;
+      rct::hash_to_p3(H_p3, rv.mixRing[i][l].dest);
+      rct::key H_l;
+      ge_p3_tobytes(H_l.bytes, &H_p3);
+      D = rct::scalarmultKey(H_l, z);  //auxilliary key image (for commitment to zero)
+      rv.p.CLSAGs[i].D = rct::scalarmultKey(D, rct::INV_EIGHT);
+      rv.p.CLSAGs[i].I = I;
+    }
+    else {
+      rv.p.CLSAGs[i].D = unsigned_tx.rct_signatures.p.CLSAGs[i].D;
+      rv.p.CLSAGs[i].I = I;
+      D = rct::scalarmultKey(rv.p.CLSAGs[i].D, rct::EIGHT);
+    }
+
+    if (not CLSAG_contexts[i].init(P, C_nonzero, C_offset, message, I, D, l, s, kAlphaComponents))
+      return false;
+
+    if (not reconstruction) {
+      rct::key mu_P;
+      rct::key mu_C;
+      if (not CLSAG_contexts[i].get_mu(mu_P, mu_C))
+        return false;
+      sc_mul(cached_w[i].bytes, mu_P.bytes, input_secret_keys[i].bytes);
+      sc_muladd(cached_w[i].bytes, mu_C.bytes, z.bytes, cached_w[i].bytes);
+    }
+  }
+  unsigned_tx.rct_signatures = std::move(rv);
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+//----------------------------------------------------------------------------------------------------------------------
+static bool compute_tx_fee(
+  const std::vector<cryptonote::tx_source_entry>& sources,
+  const std::vector<cryptonote::tx_destination_entry>& destinations,
+  std::uint64_t& fee
+)
+{
+  boost::multiprecision::uint128_t in_amount = 0;
+  for (const auto& src: sources)
+    in_amount += src.amount;
+
+  boost::multiprecision::uint128_t out_amount = 0;
+  for (const auto& dst: destinations)
+    out_amount += dst.amount;
+
+  if (out_amount > in_amount)
+    return false;
+
+  if (in_amount - out_amount > std::numeric_limits<std::uint64_t>::max())
+    return false;
+
+  fee = static_cast<std::uint64_t>(in_amount - out_amount);
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+tx_builder_ringct_t::tx_builder_ringct_t(): initialized(false) {}
+//----------------------------------------------------------------------------------------------------------------------
+tx_builder_ringct_t::~tx_builder_ringct_t()
+{
+  memwipe(static_cast<rct::key *>(cached_w.data()), cached_w.size() * sizeof(rct::key));
+}
+//----------------------------------------------------------------------------------------------------------------------
+bool tx_builder_ringct_t::init(
+  const cryptonote::account_keys& account_keys,
+  const std::vector<std::uint8_t>& extra,
+  const std::uint64_t unlock_time,
+  const std::uint32_t subaddr_account,
+  const std::set<std::uint32_t>& subaddr_minor_indices,
+  std::vector<cryptonote::tx_source_entry>& sources,
+  std::vector<cryptonote::tx_destination_entry>& destinations,
+  const cryptonote::tx_destination_entry& change,
+  const rct::RCTConfig& rct_config,
+  const bool use_rct,
+  const bool reconstruction,
+  crypto::secret_key& tx_secret_key,
+  std::vector<crypto::secret_key>& tx_aux_secret_keys,
+  cryptonote::transaction& unsigned_tx
+)
+{
+  initialized = false;
+  this->reconstruction = reconstruction;
+  if (not use_rct)
+    return false;
+  if (sources.empty())
+    return false;
+
+  if (not reconstruction)
+    unsigned_tx.set_null();
+
+  std::uint64_t fee;
+  if (not compute_tx_fee(sources, destinations, fee))
+    return false;
+
+  // decide if view tags are needed
+  const bool use_view_tags{view_tag_required(rct_config.bp_version)};
+
+  // misc. fields
+  unsigned_tx.version = 2;  //rct = 2
+  unsigned_tx.unlock_time = unlock_time;
+
+  // sort inputs
+  sort_sources(sources);
+
+  // get secret keys for signing input CLSAGs (multisig: or for the initial partial signature)
+  rct::keyV input_secret_keys;
+  auto input_secret_keys_wiper = epee::misc_utils::create_scope_leave_handler([&]{
+    memwipe(static_cast<rct::key *>(input_secret_keys.data()), input_secret_keys.size() * sizeof(rct::key));
+  });
+  if (not compute_keys_for_sources(account_keys, sources, subaddr_account, subaddr_minor_indices, input_secret_keys))
+    return false;
+
+  // randomize output order
+  if (not reconstruction)
+    shuffle_destinations(destinations);
+
+  // prepare outputs
+  rct::keyV output_public_keys;
+  rct::keyV output_amount_secret_keys;
+  std::vector<crypto::view_tag> view_tags;
+  auto output_amount_secret_keys_wiper = epee::misc_utils::create_scope_leave_handler([&]{
+    memwipe(static_cast<rct::key *>(output_amount_secret_keys.data()), output_amount_secret_keys.size() * sizeof(rct::key));
+  });
+  if (not compute_keys_for_destinations(account_keys,
+      subaddr_account,
+      destinations,
+      change,
+      extra,
+      use_view_tags,
+      reconstruction,
+      tx_secret_key,
+      tx_aux_secret_keys,
+      output_public_keys,
+      output_amount_secret_keys,
+      view_tags,
+      unsigned_tx))
+    return false;
+
+  // add inputs to tx
+  set_tx_inputs(sources, unsigned_tx);
+
+  // add output one-time addresses to tx
+  bool set_tx_outputs_result{false};
+  if (use_view_tags)
+    set_tx_outputs_result = set_tx_outputs_with_view_tags(output_public_keys, view_tags, unsigned_tx);
+  else
+    set_tx_outputs_result = set_tx_outputs(output_public_keys, unsigned_tx);
+
+  if (not set_tx_outputs_result)
+    return false;
+
+  // prepare input signatures
+  if (not set_tx_rct_signatures(fee, sources, destinations, input_secret_keys, output_public_keys, output_amount_secret_keys,
+      rct_config, reconstruction, unsigned_tx, CLSAG_contexts, cached_w))
+    return false;
+
+  initialized = true;
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+bool tx_builder_ringct_t::first_partial_sign(
+  const std::size_t source,
+  const rct::keyV& total_alpha_G,
+  const rct::keyV& total_alpha_H,
+  const rct::keyV& alpha,
+  rct::key& c_0,
+  rct::key& s
+)
+{
+  if (not initialized or reconstruction)
+    return false;
+  const std::size_t num_sources = CLSAG_contexts.size();
+  if (source >= num_sources)
+    return false;
+  rct::key c;
+  rct::key alpha_combined;
+  auto alpha_combined_wiper = epee::misc_utils::create_scope_leave_handler([&]{
+    memwipe(static_cast<rct::key *>(&alpha_combined), sizeof(rct::key));
+  });
+  if (not CLSAG_contexts[source].combine_alpha_and_compute_challenge(
+    total_alpha_G,
+    total_alpha_H,
+    alpha,
+    alpha_combined,
+    c_0,
+    c
+  )) {
+    return false;
+  }
+
+  // initial partial response:
+  //      s = alpha_combined_local - challenge*[mu_P*(local keys and sender-receiver secret and subaddress material) +
+  //                                            mu_C*(commitment-to-zero secret)]
+  sc_mulsub(s.bytes, c.bytes, cached_w[source].bytes, alpha_combined.bytes);
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+bool tx_builder_ringct_t::next_partial_sign(
+  const rct::keyM& total_alpha_G,
+  const rct::keyM& total_alpha_H,
+  const rct::keyM& alpha,
+  const rct::key& x,
+  rct::keyV& c_0,
+  rct::keyV& s
+)
+{
+  if (not initialized or not reconstruction)
+    return false;
+  const std::size_t num_sources = CLSAG_contexts.size();
+  if (num_sources != total_alpha_G.size())
+    return false;
+  if (num_sources != total_alpha_H.size())
+    return false;
+  if (num_sources != alpha.size())
+    return false;
+  if (num_sources != c_0.size())
+    return false;
+  if (num_sources != s.size())
+    return false;
+  for (std::size_t i = 0; i < num_sources; ++i) {
+    rct::key c;
+    rct::key alpha_combined;
+    auto alpha_combined_wiper = epee::misc_utils::create_scope_leave_handler([&]{
+      memwipe(static_cast<rct::key *>(&alpha_combined), sizeof(rct::key));
+    });
+    if (not CLSAG_contexts[i].combine_alpha_and_compute_challenge(
+      total_alpha_G[i],
+      total_alpha_H[i],
+      alpha[i],
+      alpha_combined,
+      c_0[i],
+      c
+    )) {
+      return false;
+    }
+    rct::key mu_P;
+    rct::key mu_C;
+    if (not CLSAG_contexts[i].get_mu(mu_P, mu_C))
+      return false;
+    rct::key w;
+    auto w_wiper = epee::misc_utils::create_scope_leave_handler([&]{
+      memwipe(static_cast<rct::key *>(&w), sizeof(rct::key));
+    });
+    sc_mul(w.bytes, mu_P.bytes, x.bytes);
+
+    // include local signer's response:
+    //      s += alpha_combined_local - challenge*[mu_P*(local keys)]
+    sc_add(s[i].bytes, s[i].bytes, alpha_combined.bytes);
+    sc_mulsub(s[i].bytes, c.bytes, w.bytes, s[i].bytes);
+  }
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+bool tx_builder_ringct_t::finalize_tx(
+  const std::vector<cryptonote::tx_source_entry>& sources,
+  const rct::keyV& c_0,
+  const rct::keyV& s,
+  cryptonote::transaction& unsigned_tx
+)
+{
+  const std::size_t num_sources = sources.size();
+  if (num_sources != unsigned_tx.rct_signatures.p.CLSAGs.size())
+    return false;
+  if (num_sources != c_0.size())
+    return false;
+  if (num_sources != s.size())
+    return false;
+  for (std::size_t i = 0; i < num_sources; ++i) {
+    const std::size_t ring_size = unsigned_tx.rct_signatures.p.CLSAGs[i].s.size();
+    if (sources[i].real_output >= ring_size)
+      return false;
+    unsigned_tx.rct_signatures.p.CLSAGs[i].s[sources[i].real_output] = s[i];
+    unsigned_tx.rct_signatures.p.CLSAGs[i].c1 = c_0[i];
+  }
+  return true;
+}
+//----------------------------------------------------------------------------------------------------------------------
+} //namespace signing
+
+} //namespace multisig
```

### src/multisig/multisig_tx_builder_ringct.h
```diff
@@ -0,0 +1,119 @@
+// Copyright (c) 2021, The Monero Project
+// 
+// All rights reserved.
+// 
+// Redistribution and use in source and binary forms, with or without modification, are
+// permitted provided that the following conditions are met:
+// 
+// 1. Redistributions of source code must retain the above copyright notice, this list of
+//    conditions and the following disclaimer.
+// 
+// 2. Redistributions in binary form must reproduce the above copyright notice, this list
+//    of conditions and the following disclaimer in the documentation and/or other
+//    materials provided with the distribution.
+// 
+// 3. Neither the name of the copyright holder nor the names of its contributors may be
+//    used to endorse or promote products derived from this software without specific
+//    prior written permission.
+// 
+// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
+// EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
+// MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
+// THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
+// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
+// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
+// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
+// STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
+// THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
+
+
+#pragma once
+
+#include "ringct/rctTypes.h"
+
+#include <set>
+#include <vector>
+
+namespace cryptonote {
+
+class transaction;
+struct tx_source_entry;
+struct tx_destination_entry;
+struct account_keys;
+
+}
+
+namespace multisig {
+
+namespace signing {
+
+class CLSAG_context_t;
+
+// number of parallel signing nonces to use per signer (2 nonces as in musig2 and FROST)
+constexpr std::size_t kAlphaComponents = 2;
+
+class tx_builder_ringct_t final {
+private:
+  // the tx builder has been initialized
+  bool initialized;
+  // the tx builder is 'reconstructing' a tx that has already been created using this object
+  bool reconstruction;
+  // cached: mu_P*(local keys and sender-receiver secret and subaddress material) + mu_C*(commitment-to-zero secret)
+  // - these are only used for the initial building of a tx (not reconstructions)                                           
+  rct::keyV cached_w;
+  // contexts for making CLSAG challenges with multisig nonces
+  std::vector<CLSAG_context_t> CLSAG_contexts;
+public:
+  tx_builder_ringct_t();
+  ~tx_builder_ringct_t();
+
+  // prepare an unsigned transaction (and get tx privkeys for outputs)
+  bool init(
+    const cryptonote::account_keys& account_keys,
+    const std::vector<std::uint8_t>& extra,
+    const std::uint64_t unlock_time,
+    const std::uint32_t subaddr_account,
+    const std::set<std::uint32_t>& subaddr_minor_indices,
+    std::vector<cryptonote::tx_source_entry>& sources,
+    std::vector<cryptonote::tx_destination_entry>& destinations,
+    const cryptonote::tx_destination_entry& change,
+    const rct::RCTConfig& rct_config,
+    const bool use_rct,
+    const bool reconstruction,
+    crypto::secret_key& tx_secret_key,
+    std::vector<crypto::secret_key>& tx_aux_secret_keys,
+    cryptonote::transaction& unsigned_tx
+  );
+
+  // get the first partial signature for the specified input ('source')
+  bool first_partial_sign(
+    const std::size_t source,
+    const rct::keyV& total_alpha_G,
+    const rct::keyV& total_alpha_H,
+    const rct::keyV& alpha,
+    rct::key& c_0,
+    rct::key& s
+  );
+
+  // get intermediate partial signatures for all the inputs
+  bool next_partial_sign(
+    const rct::keyM& total_alpha_G,
+    const rct::keyM& total_alpha_H,
+    const rct::keyM& alpha,
+    const rct::key& x,
+    rct::keyV& c_0,
+    rct::keyV& s
+  );
+
+  // finalize an unsigned transaction (add challenges and real responses to incomplete CLSAG signatures)
+  static bool finalize_tx(
+    const std::vector<cryptonote::tx_source_entry>& sources,
+    const rct::keyV& c_0,
+    const rct::keyV& s,
+    cryptonote::transaction& unsigned_tx
+  );
+};
+
+} //namespace signing
+
+} //namespace multisig
```

### src/ringct/rctSigs.cpp
```diff
@@ -238,14 +238,12 @@ namespace rct {
     //   P[l] == p*G
     //   C[l] == z*G
     //   C[i] == C_nonzero[i] - C_offset (for hashing purposes) for all i
-    clsag CLSAG_Gen(const key &message, const keyV & P, const key & p, const keyV & C, const key & z, const keyV & C_nonzero, const key & C_offset, const unsigned int l, const multisig_kLRki *kLRki, key *mscout, key *mspout, hw::device &hwdev) {
+    clsag CLSAG_Gen(const key &message, const keyV & P, const key & p, const keyV & C, const key & z, const keyV & C_nonzero, const key & C_offset, const unsigned int l, hw::device &hwdev) {
         clsag sig;
         size_t n = P.size(); // ring size
         CHECK_AND_ASSERT_THROW_MES(n == C.size(), "Signing and commitment key vector sizes must match!");
         CHECK_AND_ASSERT_THROW_MES(n == C_nonzero.size(), "Signing and commitment key vector sizes must match!");
         CHECK_AND_ASSERT_THROW_MES(l < n, "Signing index out of range!");
-        CHECK_AND_ASSERT_THROW_MES((kLRki && mscout) || (!kLRki && !mscout), "Only one of kLRki/mscout is present");
-        CHECK_AND_ASSERT_THROW_MES((mscout && mspout) || !kLRki, "Multisig pointers are not all present");
 
         // Key images
         ge_p3 H_p3;
@@ -260,16 +258,7 @@ namespace rct {
         key aG;
         key aH;
 
-        // Multisig
-        if (kLRki)
-        {
-            sig.I = kLRki->ki;
-            scalarmultKey(D,H,z);
-        }
-        else
-        {
-            hwdev.clsag_prepare(p,z,sig.I,D,H,a,aG,aH);
-        }
+        hwdev.clsag_prepare(p,z,sig.I,D,H,a,aG,aH);
 
         geDsmp I_precomp;
         geDsmp D_precomp;
@@ -317,18 +306,9 @@ namespace rct {
         c_to_hash[2*n+1] = C_offset;
         c_to_hash[2*n+2] = message;
 
-        // Multisig data is present
-        if (kLRki)
-        {
-            a = kLRki->k;
-            c_to_hash[2*n+3] = kLRki->L;
-            c_to_hash[2*n+4] = kLRki->R;
-        }
-        else
-        {
-            c_to_hash[2*n+3] = aG;
-            c_to_hash[2*n+4] = aH;
-        }
+        c_to_hash[2*n+3] = aG;
+        c_to_hash[2*n+4] = aH;
+
         hwdev.clsag_hash(c_to_hash,c);
         
         size_t i;
@@ -380,24 +360,19 @@ namespace rct {
         hwdev.clsag_sign(c,a,p,z,mu_P,mu_C,sig.s[l]);
         memwipe(&a, sizeof(key));
 
-        if (mscout)
-          *mscout = c;
-        if (mspout)
-          *mspout = mu_P;
-
         return sig;
     }
 
     clsag CLSAG_Gen(const key &message, const keyV & P, const key & p, const keyV & C, const key & z, const keyV & C_nonzero, const key & C_offset, const unsigned int l) {
-        return CLSAG_Gen(message, P, p, C, z, C_nonzero, C_offset, l, NULL, NULL, NULL, hw::get_device("default"));
+        return CLSAG_Gen(message, P, p, C, z, C_nonzero, C_offset, l, hw::get_device("default"));
     }
 
     // MLSAG signatures
     // See paper by Noether (https://eprint.iacr.org/2015/1098)
     // This generalization allows for some dimensions not to require linkability;
     //   this is used in practice for commitment data within signatures
     // Note that using more than one linkable dimension is not recommended.
-    mgSig MLSAG_Gen(const key &message, const keyM & pk, const keyV & xx, const multisig_kLRki *kLRki, key *mscout, const unsigned int index, size_t dsRows, hw::device &hwdev) {
+    mgSig MLSAG_Gen(const key &message, const keyM & pk, const keyV & xx, const unsigned int index, size_t dsRows, hw::device &hwdev) {
         mgSig rv;
         size_t cols = pk.size();
         CHECK_AND_ASSERT_THROW_MES(cols >= 2, "Error! What is c if cols = 1!");
@@ -409,8 +384,6 @@ namespace rct {
         }
         CHECK_AND_ASSERT_THROW_MES(xx.size() == rows, "Bad xx size");
         CHECK_AND_ASSERT_THROW_MES(dsRows <= rows, "Bad dsRows size");
-        CHECK_AND_ASSERT_THROW_MES((kLRki && mscout) || (!kLRki && !mscout), "Only one of kLRki/mscout is present");
-        CHECK_AND_ASSERT_THROW_MES(!kLRki || dsRows == 1, "Multisig requires exactly 1 dsRows");
 
         size_t i = 0, j = 0, ii = 0;
         key c, c_old, L, R, Hi;
@@ -428,20 +401,11 @@ namespace rct {
         DP("here1");
         for (i = 0; i < dsRows; i++) {
             toHash[3 * i + 1] = pk[index][i];
-            if (kLRki) {
-              // multisig
-              alpha[i] = kLRki->k;
-              toHash[3 * i + 2] = kLRki->L;
-              toHash[3 * i + 3] = kLRki->R;
-              rv.II[i] = kLRki->ki;
-            }
-            else {
-              hash_to_p3(Hi_p3, pk[index][i]);
-              ge_p3_tobytes(Hi.bytes, &Hi_p3);
-              hwdev.mlsag_prepare(Hi, xx[i], alpha[i] , aG[i] , aHP[i] , rv.II[i]);
-              toHash[3 * i + 2] = aG[i];
-              toHash[3 * i + 3] = aHP[i];
-            }
+            hash_to_p3(Hi_p3, pk[index][i]);
+            ge_p3_tobytes(Hi.bytes, &Hi_p3);
+            hwdev.mlsag_prepare(Hi, xx[i], alpha[i] , aG[i] , aHP[i] , rv.II[i]);
+            toHash[3 * i + 2] = aG[i];
+            toHash[3 * i + 3] = aHP[i];
             precomp(Ip[i].k, rv.II[i]);
         }
         size_t ndsRows = 3 * dsRows; //non Double Spendable Rows (see identity chains paper)
@@ -485,8 +449,6 @@ namespace rct {
             }   
         }
         hwdev.mlsag_sign(c, xx, alpha, rows, dsRows, rv.ss[index]);
-        if (mscout)
-          *mscout = c;
         return rv;
     }
     
@@ -722,7 +684,7 @@ namespace rct {
     //   this shows that sum inputs = sum outputs
     //Ver:    
     //   verifies the above sig is created corretly
-    mgSig proveRctMG(const key &message, const ctkeyM & pubs, const ctkeyV & inSk, const ctkeyV &outSk, const ctkeyV & outPk, const multisig_kLRki *kLRki, key *mscout, unsigned int index, const key &txnFeeKey, hw::device &hwdev) {
+    mgSig proveRctMG(const key &message, const ctkeyM & pubs, const ctkeyV & inSk, const ctkeyV &outSk, const ctkeyV & outPk, unsigned int index, const key &txnFeeKey, hw::device &hwdev) {
         //setup vars
         size_t cols = pubs.size();
         CHECK_AND_ASSERT_THROW_MES(cols >= 1, "Empty pubs");
@@ -733,7 +695,6 @@ namespace rct {
         }
         CHECK_AND_ASSERT_THROW_MES(inSk.size() == rows, "Bad inSk size");
         CHECK_AND_ASSERT_THROW_MES(outSk.size() == outPk.size(), "Bad outSk/outPk size");
-        CHECK_AND_ASSERT_THROW_MES((kLRki && mscout) || (!kLRki && !mscout), "Only one of kLRki/mscout is present");
 
         keyV sk(rows + 1);
         keyV tmp(rows + 1);
@@ -766,7 +727,7 @@ namespace rct {
         for (size_t j = 0; j < outPk.size(); j++) {
             sc_sub(sk[rows].bytes, sk[rows].bytes, outSk[j].mask.bytes); //subtract output masks in last row..
         }
-        mgSig result = MLSAG_Gen(message, M, sk, kLRki, mscout, index, rows, hwdev);
+        mgSig result = MLSAG_Gen(message, M, sk, index, rows, hwdev);
         memwipe(sk.data(), sk.size() * sizeof(key));
         return result;
     }
@@ -779,12 +740,11 @@ namespace rct {
     //   inSk is x, a_in corresponding to signing index
     //       a_out, Cout is for the output commitment
     //       index is the signing index..
-    mgSig proveRctMGSimple(const key &message, const ctkeyV & pubs, const ctkey & inSk, const key &a , const key &Cout, const multisig_kLRki *kLRki, key *mscout, unsigned int index, hw::device &hwdev) {
+    mgSig proveRctMGSimple(const key &message, const ctkeyV & pubs, const ctkey & inSk, const key &a , const key &Cout, unsigned int index, hw::device &hwdev) {
         //setup vars
         size_t rows = 1;
         size_t cols = pubs.size();
         CHECK_AND_ASSERT_THROW_MES(cols >= 1, "Empty pubs");
-        CHECK_AND_ASSERT_THROW_MES((kLRki && mscout) || (!kLRki && !mscout), "Only one of kLRki/mscout is present");
         keyV tmp(rows + 1);
         keyV sk(rows + 1);
         size_t i;
@@ -796,17 +756,16 @@ namespace rct {
             M[i][0] = pubs[i].dest;
             subKeys(M[i][1], pubs[i].mask, Cout);
         }
-        mgSig result = MLSAG_Gen(message, M, sk, kLRki, mscout, index, rows, hwdev);
+        mgSig result = MLSAG_Gen(message, M, sk, index, rows, hwdev);
         memwipe(sk.data(), sk.size() * sizeof(key));
         return result;
     }
 
-    clsag proveRctCLSAGSimple(const key &message, const ctkeyV &pubs, const ctkey &inSk, const key &a, const key &Cout, const multisig_kLRki *kLRki, key *mscout, key *mspout, unsigned int index, hw::device &hwdev) {
+    clsag proveRctCLSAGSimple(const key &message, const ctkeyV &pubs, const ctkey &inSk, const key &a, const key &Cout, unsigned int index, hw::device &hwdev) {
         //setup vars
         size_t rows = 1;
         size_t cols = pubs.size();
         CHECK_AND_ASSERT_THROW_MES(cols >= 1, "Empty pubs");
-        CHECK_AND_ASSERT_THROW_MES((kLRki && mscout) || (!kLRki && !mscout), "Only one of kLRki/mscout is present");
         keyV tmp(rows + 1);
         keyV sk(rows + 1);
         keyM M(cols, tmp);
@@ -826,7 +785,7 @@ namespace rct {
 
         sk[0] = copy(inSk.dest);
         sc_sub(sk[1].bytes, inSk.mask.bytes, a.bytes);
-        clsag result = CLSAG_Gen(message, P, sk[0], C, sk[1], C_nonzero, Cout, index, kLRki, mscout, mspout, hwdev);
+        clsag result = CLSAG_Gen(message, P, sk[0], C, sk[1], C_nonzero, Cout, index, hwdev);
         memwipe(sk.data(), sk.size() * sizeof(key));
         return result;
     }
@@ -1084,14 +1043,13 @@ namespace rct {
     //   must know the destination private key to find the correct amount, else will return a random number
     //   Note: For txn fees, the last index in the amounts vector should contain that
     //   Thus the amounts vector will be "one" longer than the destinations vectort
-    rctSig genRct(const key &message, const ctkeyV & inSk, const keyV & destinations, const vector<xmr_amount> & amounts, const ctkeyM &mixRing, const keyV &amount_keys, const multisig_kLRki *kLRki, multisig_out *msout, unsigned int index, ctkeyV &outSk, const RCTConfig &rct_config, hw::device &hwdev) {
+    rctSig genRct(const key &message, const ctkeyV & inSk, const keyV & destinations, const vector<xmr_amount> & amounts, const ctkeyM &mixRing, const keyV &amount_keys, unsigned int index, ctkeyV &outSk, const RCTConfig &rct_config, hw::device &hwdev) {
         CHECK_AND_ASSERT_THROW_MES(amounts.size() == destinations.size() || amounts.size() == destinations.size() + 1, "Different number of amounts/destinations");
         CHECK_AND_ASSERT_THROW_MES(amount_keys.size() == destinations.size(), "Different number of amount_keys/destinations");
         CHECK_AND_ASSERT_THROW_MES(index < mixRing.size(), "Bad index into mixRing");
         for (size_t n = 0; n < mixRing.size(); ++n) {
           CHECK_AND_ASSERT_THROW_MES(mixRing[n].size() == inSk.size(), "Bad mixRing size");
         }
-        CHECK_AND_ASSERT_THROW_MES((kLRki && msout) || (!kLRki && !msout), "Only one of kLRki/msout is present");
         CHECK_AND_ASSERT_THROW_MES(inSk.size() < 2, "genRct is not suitable for 2+ rings");
 
         rctSig rv;
@@ -1130,23 +1088,21 @@ namespace rct {
         key txnFeeKey = scalarmultH(d2h(rv.txnFee));
 
         rv.mixRing = mixRing;
-        if (msout)
-          msout->c.resize(1);
-        rv.p.MGs.push_back(proveRctMG(get_pre_mlsag_hash(rv, hwdev), rv.mixRing, inSk, outSk, rv.outPk, kLRki, msout ? &msout->c[0] : NULL, index, txnFeeKey,hwdev));
+        rv.p.MGs.push_back(proveRctMG(get_pre_mlsag_hash(rv, hwdev), rv.mixRing, inSk, outSk, rv.outPk, index, txnFeeKey,hwdev));
         return rv;
     }
 
-    rctSig genRct(const key &message, const ctkeyV & inSk, const ctkeyV  & inPk, const keyV & destinations, const vector<xmr_amount> & amounts, const keyV &amount_keys, const multisig_kLRki *kLRki, multisig_out *msout, const int mixin, const RCTConfig &rct_config, hw::device &hwdev) {
+    rctSig genRct(const key &message, const ctkeyV & inSk, const ctkeyV  & inPk, const keyV & destinations, const vector<xmr_amount> & amounts, const keyV &amount_keys, const int mixin, const RCTConfig &rct_config, hw::device &hwdev) {
         unsigned int index;
         ctkeyM mixRing;
         ctkeyV outSk;
         tie(mixRing, index) = populateFromBlockchain(inPk, mixin);
-        return genRct(message, inSk, destinations, amounts, mixRing, amount_keys, kLRki, msout, index, outSk, rct_config, hwdev);
+        return genRct(message, inSk, destinations, amounts, mixRing, amount_keys, index, outSk, rct_config, hwdev);
     }
     
     //RCT simple    
     //for post-rct only
-    rctSig genRctSimple(const key &message, const ctkeyV & inSk, const keyV & destinations, const vector<xmr_amount> &inamounts, const vector<xmr_amount> &outamounts, xmr_amount txnFee, const ctkeyM & mixRing, const keyV &amount_keys, const std::vector<multisig_kLRki> *kLRki, multisig_out *msout, const std::vector<unsigned int> & index, ctkeyV &outSk, const RCTConfig &rct_config, hw::device &hwdev) {
+    rctSig genRctSimple(const key &message, const ctkeyV & inSk, const keyV & destinations, const vector<xmr_amount> &inamounts, const vector<xmr_amount> &outamounts, xmr_amount txnFee, const ctkeyM & mixRing, const keyV &amount_keys, const std::vector<unsigned int> & index, ctkeyV &outSk, const RCTConfig &rct_config, hw::device &hwdev) {
         const bool bulletproof_or_plus = rct_config.range_proof_type > RangeProofBorromean;
         CHECK_AND_ASSERT_THROW_MES(inamounts.size() > 0, "Empty inamounts");
         CHECK_AND_ASSERT_THROW_MES(inamounts.size() == inSk.size(), "Different number of inamounts/inSk");
@@ -1157,10 +1113,6 @@ namespace rct {
         for (size_t n = 0; n < mixRing.size(); ++n) {
           CHECK_AND_ASSERT_THROW_MES(index[n] < mixRing[n].size(), "Bad index into mixRing");
         }
-        CHECK_AND_ASSERT_THROW_MES((kLRki && msout) || (!kLRki && !msout), "Only one of kLRki/msout is present");
-        if (kLRki && msout) {
-          CHECK_AND_ASSERT_THROW_MES(kLRki->size() == inamounts.size(), "Mismatched kLRki/inamounts sizes");
-        }
 
         rctSig rv;
         if (bulletproof_or_plus)
@@ -1322,29 +1274,25 @@ namespace rct {
         DP(pseudoOuts[i]);
 
         key full_message = get_pre_mlsag_hash(rv,hwdev);
-        if (msout)
-        {
-            msout->c.resize(inamounts.size());
-            msout->mu_p.resize(is_rct_clsag(rv.type) ? inamounts.size() : 0);
-        }
+
         for (i = 0 ; i < inamounts.size(); i++)
         {
             if (is_rct_clsag(rv.type))
             {
                 if (hwdev.get_mode() == hw::device::TRANSACTION_CREATE_FAKE)
                     rv.p.CLSAGs[i] = make_dummy_clsag(rv.mixRing[i].size());
                 else
-                    rv.p.CLSAGs[i] = proveRctCLSAGSimple(full_message, rv.mixRing[i], inSk[i], a[i], pseudoOuts[i], kLRki ? &(*kLRki)[i]: NULL, msout ? &msout->c[i] : NULL, msout ? &msout->mu_p[i] : NULL, index[i], hwdev);
+                    rv.p.CLSAGs[i] = proveRctCLSAGSimple(full_message, rv.mixRing[i], inSk[i], a[i], pseudoOuts[i], index[i], hwdev);
             }
             else
             {
-                rv.p.MGs[i] = proveRctMGSimple(full_message, rv.mixRing[i], inSk[i], a[i], pseudoOuts[i], kLRki ? &(*kLRki)[i]: NULL, msout ? &msout->c[i] : NULL, index[i], hwdev);
+                rv.p.MGs[i] = proveRctMGSimple(full_message, rv.mixRing[i], inSk[i], a[i], pseudoOuts[i], index[i], hwdev);
             }
         }
         return rv;
     }
 
-    rctSig genRctSimple(const key &message, const ctkeyV & inSk, const ctkeyV & inPk, const keyV & destinations, const vector<xmr_amount> &inamounts, const vector<xmr_amount> &outamounts, const keyV &amount_keys, const std::vector<multisig_kLRki> *kLRki, multisig_out *msout, xmr_amount txnFee, unsigned int mixin, const RCTConfig &rct_config, hw::device &hwdev) {
+    rctSig genRctSimple(const key &message, const ctkeyV & inSk, const ctkeyV & inPk, const keyV & destinations, const vector<xmr_amount> &inamounts, const vector<xmr_amount> &outamounts, const keyV &amount_keys, xmr_amount txnFee, unsigned int mixin, const RCTConfig &rct_config, hw::device &hwdev) {
         std::vector<unsigned int> index;
         index.resize(inPk.size());
         ctkeyM mixRing;
@@ -1354,7 +1302,7 @@ namespace rct {
           mixRing[i].resize(mixin+1);
           index[i] = populateFromBlockchainSimple(mixRing[i], inPk[i], mixin);
         }
-        return genRctSimple(message, inSk, destinations, inamounts, outamounts, txnFee, mixRing, amount_keys, kLRki, msout, index, outSk, rct_config, hwdev);
+        return genRctSimple(message, inSk, destinations, inamounts, outamounts, txnFee, mixRing, amount_keys, index, outSk, rct_config, hwdev);
     }
 
     //RingCT protocol
@@ -1700,60 +1648,4 @@ namespace rct {
       key mask;
       return decodeRctSimple(rv, sk, i, mask, hwdev);
     }
-
-    bool signMultisigMLSAG(rctSig &rv, const std::vector<unsigned int> &indices, const keyV &k, const multisig_out &msout, const key &secret_key) {
-        CHECK_AND_ASSERT_MES(rv.type == RCTTypeFull || rv.type == RCTTypeSimple || rv.type == RCTTypeBulletproof || rv.type == RCTTypeBulletproof2,
-            false, "unsupported rct type");
-        CHECK_AND_ASSERT_MES(!is_rct_clsag(rv.type), false, "CLSAG signature type in MLSAG signature function");
-        CHECK_AND_ASSERT_MES(indices.size() == k.size(), false, "Mismatched k/indices sizes");
-        CHECK_AND_ASSERT_MES(k.size() == rv.p.MGs.size(), false, "Mismatched k/MGs size");
-        CHECK_AND_ASSERT_MES(k.size() == msout.c.size(), false, "Mismatched k/msout.c size");
-        CHECK_AND_ASSERT_MES(rv.p.CLSAGs.empty(), false, "CLSAGs not empty for MLSAGs");
-        if (rv.type == RCTTypeFull)
-        {
-          CHECK_AND_ASSERT_MES(rv.p.MGs.size() == 1, false, "MGs not a single element");
-        }
-        for (size_t n = 0; n < indices.size(); ++n) {
-            CHECK_AND_ASSERT_MES(indices[n] < rv.p.MGs[n].ss.size(), false, "Index out of range");
-            CHECK_AND_ASSERT_MES(!rv.p.MGs[n].ss[indices[n]].empty(), false, "empty ss line");
-        }
-
-        // MLSAG: each player contributes a share to the secret-index ss: k - cc*secret_key_share
-        //     cc: msout.c[n], secret_key_share: secret_key
-        for (size_t n = 0; n < indices.size(); ++n) {
-            rct::key diff;
-            sc_mulsub(diff.bytes, msout.c[n].bytes, secret_key.bytes, k[n].bytes);
-            sc_add(rv.p.MGs[n].ss[indices[n]][0].bytes, rv.p.MGs[n].ss[indices[n]][0].bytes, diff.bytes);
-        }
-        return true;
-    }
-
-    bool signMultisigCLSAG(rctSig &rv, const std::vector<unsigned int> &indices, const keyV &k, const multisig_out &msout, const key &secret_key) {
-        CHECK_AND_ASSERT_MES(is_rct_clsag(rv.type), false, "unsupported rct type");
-        CHECK_AND_ASSERT_MES(indices.size() == k.size(), false, "Mismatched k/indices sizes");
-        CHECK_AND_ASSERT_MES(k.size() == rv.p.CLSAGs.size(), false, "Mismatched k/CLSAGs size");
-        CHECK_AND_ASSERT_MES(k.size() == msout.c.size(), false, "Mismatched k/msout.c size");
-        CHECK_AND_ASSERT_MES(rv.p.MGs.empty(), false, "MGs not empty for CLSAGs");
-        CHECK_AND_ASSERT_MES(msout.c.size() == msout.mu_p.size(), false, "Bad mu_p size");
-        for (size_t n = 0; n < indices.size(); ++n) {
-            CHECK_AND_ASSERT_MES(indices[n] < rv.p.CLSAGs[n].s.size(), false, "Index out of range");
-        }
-
-        // CLSAG: each player contributes a share to the secret-index ss: k - cc*mu_p*secret_key_share
-        // cc: msout.c[n], mu_p, msout.mu_p[n], secret_key_share: secret_key
-        for (size_t n = 0; n < indices.size(); ++n) {
-            rct::key diff, sk;
-            sc_mul(sk.bytes, msout.mu_p[n].bytes, secret_key.bytes);
-            sc_mulsub(diff.bytes, msout.c[n].bytes, sk.bytes, k[n].bytes);
-            sc_add(rv.p.CLSAGs[n].s[indices[n]].bytes, rv.p.CLSAGs[n].s[indices[n]].bytes, diff.bytes);
-        }
-        return true;
-    }
-
-    bool signMultisig(rctSig &rv, const std::vector<unsigned int> &indices, const keyV &k, const multisig_out &msout, const key &secret_key) {
-        if (is_rct_clsag(rv.type))
-            return signMultisigCLSAG(rv, indices, k, msout, secret_key);
-        else
-            return signMultisigMLSAG(rv, indices, k, msout, secret_key);
-    }
 }
```

### src/ringct/rctSigs.h
```diff
@@ -74,12 +74,12 @@ namespace rct {
     // Gen creates a signature which proves that for some column in the keymatrix "pk"
     //   the signer knows a secret key for each row in that column
     // Ver verifies that the MG sig was created correctly
-    mgSig MLSAG_Gen(const key &message, const keyM & pk, const keyV & xx, const multisig_kLRki *kLRki, key *mscout, const unsigned int index, size_t dsRows, hw::device &hwdev);
+    mgSig MLSAG_Gen(const key &message, const keyM & pk, const keyV & xx, const unsigned int index, size_t dsRows, hw::device &hwdev);
     bool MLSAG_Ver(const key &message, const keyM &pk, const mgSig &sig, size_t dsRows);
 
-    clsag CLSAG_Gen(const key &message, const keyV & P, const key & p, const keyV & C, const key & z, const keyV & C_nonzero, const key & C_offset, const unsigned int l, const multisig_kLRki *kLRki, key *mscout, key *mspout, hw::device &hwdev);
+    clsag CLSAG_Gen(const key &message, const keyV & P, const key & p, const keyV & C, const key & z, const keyV & C_nonzero, const key & C_offset, const unsigned int l, hw::device &hwdev);
     clsag CLSAG_Gen(const key &message, const keyV & P, const key & p, const keyV & C, const key & z, const keyV & C_nonzero, const key & C_offset, const unsigned int l);
-    clsag proveRctCLSAGSimple(const key &, const ctkeyV &, const ctkey &, const key &, const key &, const multisig_kLRki *, key *, key *, unsigned int, hw::device &);
+    clsag proveRctCLSAGSimple(const key &, const ctkeyV &, const ctkey &, const key &, const key &, unsigned int, hw::device &);
     bool verRctCLSAGSimple(const key &, const clsag &, const ctkeyV &, const key &);
 
     //proveRange and verRange
@@ -100,8 +100,8 @@ namespace rct {
     //   this shows that sum inputs = sum outputs
     //Ver:
     //   verifies the above sig is created corretly
-    mgSig proveRctMG(const ctkeyM & pubs, const ctkeyV & inSk, const keyV &outMasks, const ctkeyV & outPk, const multisig_kLRki *kLRki, key *mscout, unsigned int index, const key &txnFee, const key &message, hw::device &hwdev);
-    mgSig proveRctMGSimple(const key & message, const ctkeyV & pubs, const ctkey & inSk, const key &a , const key &Cout, const multisig_kLRki *kLRki, key *mscout, unsigned int index, hw::device &hwdev);
+    mgSig proveRctMG(const ctkeyM & pubs, const ctkeyV & inSk, const keyV &outMasks, const ctkeyV & outPk, unsigned int index, const key &txnFee, const key &message, hw::device &hwdev);
+    mgSig proveRctMGSimple(const key & message, const ctkeyV & pubs, const ctkey & inSk, const key &a , const key &Cout, unsigned int index, hw::device &hwdev);
     bool verRctMG(const mgSig &mg, const ctkeyM & pubs, const ctkeyV & outPk, const key &txnFee, const key &message);
     bool verRctMGSimple(const key &message, const mgSig &mg, const ctkeyV & pubs, const key & C);
 
@@ -123,10 +123,10 @@ namespace rct {
     //decodeRct: (c.f. https://eprint.iacr.org/2015/1098 section 5.1.1)
     //   uses the attached ecdh info to find the amounts represented by each output commitment
     //   must know the destination private key to find the correct amount, else will return a random number
-    rctSig genRct(const key &message, const ctkeyV & inSk, const keyV & destinations, const std::vector<xmr_amount> & amounts, const ctkeyM &mixRing, const keyV &amount_keys, const multisig_kLRki *kLRki, multisig_out *msout, unsigned int index, ctkeyV &outSk, const RCTConfig &rct_config, hw::device &hwdev);
-    rctSig genRct(const key &message, const ctkeyV & inSk, const ctkeyV  & inPk, const keyV & destinations, const std::vector<xmr_amount> & amounts, const keyV &amount_keys, const multisig_kLRki *kLRki, multisig_out *msout, const int mixin, const RCTConfig &rct_config, hw::device &hwdev);
-    rctSig genRctSimple(const key & message, const ctkeyV & inSk, const ctkeyV & inPk, const keyV & destinations, const std::vector<xmr_amount> & inamounts, const std::vector<xmr_amount> & outamounts, const keyV &amount_keys, const std::vector<multisig_kLRki> *kLRki, multisig_out *msout, xmr_amount txnFee, unsigned int mixin, const RCTConfig &rct_config, hw::device &hwdev);
-    rctSig genRctSimple(const key & message, const ctkeyV & inSk, const keyV & destinations, const std::vector<xmr_amount> & inamounts, const std::vector<xmr_amount> & outamounts, xmr_amount txnFee, const ctkeyM & mixRing, const keyV &amount_keys, const std::vector<multisig_kLRki> *kLRki, multisig_out *msout, const std::vector<unsigned int> & index, ctkeyV &outSk, const RCTConfig &rct_config, hw::device &hwdev);
+    rctSig genRct(const key &message, const ctkeyV & inSk, const keyV & destinations, const std::vector<xmr_amount> & amounts, const ctkeyM &mixRing, const keyV &amount_keys, unsigned int index, ctkeyV &outSk, const RCTConfig &rct_config, hw::device &hwdev);
+    rctSig genRct(const key &message, const ctkeyV & inSk, const ctkeyV  & inPk, const keyV & destinations, const std::vector<xmr_amount> & amounts, const keyV &amount_keys, const int mixin, const RCTConfig &rct_config, hw::device &hwdev);
+    rctSig genRctSimple(const key & message, const ctkeyV & inSk, const ctkeyV & inPk, const keyV & destinations, const std::vector<xmr_amount> & inamounts, const std::vector<xmr_amount> & outamounts, const keyV &amount_keys, xmr_amount txnFee, unsigned int mixin, const RCTConfig &rct_config, hw::device &hwdev);
+    rctSig genRctSimple(const key & message, const ctkeyV & inSk, const keyV & destinations, const std::vector<xmr_amount> & inamounts, const std::vector<xmr_amount> & outamounts, xmr_amount txnFee, const ctkeyM & mixRing, const keyV &amount_keys, const std::vector<unsigned int> & index, ctkeyV &outSk, const RCTConfig &rct_config, hw::device &hwdev);
     bool verRct(const rctSig & rv, bool semantics);
     static inline bool verRct(const rctSig & rv) { return verRct(rv, true) && verRct(rv, false); }
     bool verRctSemanticsSimple(const rctSig & rv);
@@ -138,7 +138,6 @@ namespace rct {
     xmr_amount decodeRctSimple(const rctSig & rv, const key & sk, unsigned int i, key & mask, hw::device &hwdev);
     xmr_amount decodeRctSimple(const rctSig & rv, const key & sk, unsigned int i, hw::device &hwdev);
     key get_pre_mlsag_hash(const rctSig &rv, hw::device &hwdev);
-    bool signMultisig(rctSig &rv, const std::vector<unsigned int> &indices, const keyV &k, const multisig_out &msout, const key &secret_key);
 }
 #endif  /* RCTSIGS_H */
 
```

### src/wallet/wallet2.cpp
```diff
@@ -62,6 +62,7 @@ using namespace epee;
 #include "multisig/multisig.h"
 #include "multisig/multisig_account.h"
 #include "multisig/multisig_kex_msg.h"
+#include "multisig/multisig_tx_builder_ringct.h"
 #include "common/boost_serialization_helper.h"
 #include "common/command_line.h"
 #include "common/threadpool.h"
@@ -5070,7 +5071,6 @@ std::string wallet2::make_multisig(const epee::wipeable_string &password,
   m_multisig_rounds_passed = 1;
 
   // derivations stored (should be empty in last round)
-  // TODO: make use of the origins map for aggregation-style signing (instead of round-robin)
   m_multisig_derivations.clear();
   m_multisig_derivations.reserve(multisig_account.get_kex_keys_to_origins_map().size());
 
@@ -5127,7 +5127,6 @@ std::string wallet2::exchange_multisig_keys(const epee::wipeable_string &passwor
     expanded_msgs.emplace_back(msg);
 
   // reconstruct multisig account
-  crypto::public_key dummy;
   multisig::multisig_keyset_map_memsafe_t kex_origins_map;
 
   for (const auto &derivation : m_multisig_derivations)
@@ -5163,7 +5162,6 @@ std::string wallet2::exchange_multisig_keys(const epee::wipeable_string &passwor
       "Failed to update multisig wallet account due to bad keys");
 
   // derivations stored (should be empty in last round)
-  // TODO: make use of the origins map for aggregation-style signing (instead of round-robin)
   m_multisig_derivations.clear();
   m_multisig_derivations.reserve(multisig_account.get_kex_keys_to_origins_map().size());
 
@@ -6642,8 +6640,7 @@ bool wallet2::sign_tx(unsigned_tx_set &exported_txs, std::vector<wallet2::pendin
     rct::RCTConfig rct_config = sd.rct_config;
     crypto::secret_key tx_key;
     std::vector<crypto::secret_key> additional_tx_keys;
-    rct::multisig_out msout;
-    bool r = cryptonote::construct_tx_and_get_tx_key(m_account.get_keys(), m_subaddresses, sd.sources, sd.splitted_dsts, sd.change_dts.addr, sd.extra, ptx.tx, sd.unlock_time, tx_key, additional_tx_keys, sd.use_rct, rct_config, m_multisig ? &msout : NULL, sd.use_view_tags);
+    bool r = cryptonote::construct_tx_and_get_tx_key(m_account.get_keys(), m_subaddresses, sd.sources, sd.splitted_dsts, sd.change_dts.addr, sd.extra, ptx.tx, sd.unlock_time, tx_key, additional_tx_keys, sd.use_rct, rct_config, sd.use_view_tags);
     THROW_WALLET_EXCEPTION_IF(!r, error::tx_not_constructed, sd.sources, sd.splitted_dsts, sd.unlock_time, m_nettype);
     // we don't test tx size, because we don't know the current limit, due to not having a blockchain,
     // and it's a bit pointless to fail there anyway, since it'd be a (good) guess only. We sign anyway,
@@ -7151,77 +7148,113 @@ bool wallet2::sign_multisig_tx(multisig_tx_set &exported_txs, std::vector<crypto
 
   txids.clear();
 
-  // sign the transactions
+  // The 'exported_txs' contains a set of different transactions for the multisig group to try to sign. Each of those
+  //   transactions has a set of 'signing attempts' corresponding to all the possible signing groups within the multisig.
+  // - Here, we will partially sign as many of those signing attempts as possible, for each proposed transaction.
   for (size_t n = 0; n < exported_txs.m_ptx.size(); ++n)
   {
     tools::wallet2::pending_tx &ptx = exported_txs.m_ptx[n];
     THROW_WALLET_EXCEPTION_IF(ptx.multisig_sigs.empty(), error::wallet_internal_error, "No signatures found in multisig tx");
-    tools::wallet2::tx_construction_data &sd = ptx.construction_data;
-    LOG_PRINT_L1(" " << (n+1) << ": " << sd.sources.size() << " inputs, mixin " << (sd.sources[0].outputs.size()-1) <<
+    const tools::wallet2::tx_construction_data &sd = ptx.construction_data;
+    LOG_PRINT_L1(" " << (n+1) << ": " << sd.sources.size() << " inputs, ring size " << (sd.sources[0].outputs.size()) <<
         ", signed by " << exported_txs.m_signers.size() << "/" << m_multisig_threshold);
-    cryptonote::transaction tx;
-    rct::multisig_out msout = ptx.multisig_sigs.front().msout;
-    auto sources = sd.sources;
-    rct::RCTConfig rct_config = sd.rct_config;
-    bool shuffle_outs = false;
-    bool r = cryptonote::construct_tx_with_tx_key(m_account.get_keys(), m_subaddresses, sources, sd.splitted_dsts, ptx.change_dts.addr, sd.extra, tx, sd.unlock_time, ptx.tx_key, ptx.additional_tx_keys, sd.use_rct, rct_config, &msout, shuffle_outs, sd.use_view_tags);
-    THROW_WALLET_EXCEPTION_IF(!r, error::tx_not_constructed, sd.sources, sd.splitted_dsts, sd.unlock_time, m_nettype);
-
-    THROW_WALLET_EXCEPTION_IF(get_transaction_prefix_hash (tx) != get_transaction_prefix_hash(ptx.tx),
-        error::wallet_internal_error, "Transaction prefix does not match data");
 
-    // Tests passed, sign
-    std::vector<unsigned int> indices;
-    for (const auto &source: sources)
-      indices.push_back(source.real_output);
+    // reconstruct the partially-signed transaction attempt to verify we are signing something that at least looks like a transaction
+    // note: the caller should further verify that the tx details are acceptable (inputs/outputs/memos/tx type)
+    multisig::signing::tx_builder_ringct_t multisig_tx_builder;
+    THROW_WALLET_EXCEPTION_IF(
+      not multisig_tx_builder.init(
+        m_account.get_keys(),
+        ptx.construction_data.extra,
+        ptx.construction_data.unlock_time,
+        ptx.construction_data.subaddr_account,
+        ptx.construction_data.subaddr_indices,
+        ptx.construction_data.sources,
+        ptx.construction_data.splitted_dsts,
+        ptx.construction_data.change_dts,
+        ptx.construction_data.rct_config,
+        ptx.construction_data.use_rct,
+        true,  //true = we are reconstructing the tx (it was first constructed by the tx proposer)
+        ptx.tx_key,
+        ptx.additional_tx_keys,
+        ptx.tx
+      ),
+      error::wallet_internal_error,
+      "error: multisig::signing::tx_builder_ringct_t::init"
+    );
 
+    // go through each signing attempt for this transaction (each signing attempt corresponds to some subgroup of signers
+    //   of size 'threshold')
     for (auto &sig: ptx.multisig_sigs)
     {
+      // skip this partial tx if it's intended for a subgroup of signers that doesn't include the local signer
+      // note: this check can only weed out signers who provided multisig_infos to the multisig tx proposer's
+      //       (initial author's) last call to import_multisig() before making this tx proposal; all other signers
+      //       will encounter a 'need to export multisig' wallet error in get_multisig_k() below
+      // note2: the 'need to export multisig' wallet error can also appear if a bad/buggy tx proposer adds duplicate
+      //       'used_L' to the set of tx attempts, or if two different tx proposals use the same 'used_L' values and the
+      //       local signer calls this function on both of them
       if (sig.ignore.find(local_signer) == sig.ignore.end())
       {
-        ptx.tx.rct_signatures = sig.sigs;
-
-        rct::keyV k;
+        rct::keyM local_nonces_k(sd.selected_transfers.size(), rct::keyV(multisig::signing::kAlphaComponents));
         rct::key skey = rct::zero();
-        auto wiper = epee::misc_utils::create_scope_leave_handler([&](){ memwipe(k.data(), k.size() * sizeof(k[0])); memwipe(&skey, sizeof(skey)); });
-
-        for (size_t idx: sd.selected_transfers)
-          k.push_back(get_multisig_k(idx, sig.used_L));
+        auto wiper = epee::misc_utils::create_scope_leave_handler([&]{
+          for (auto& e: local_nonces_k)
+            memwipe(e.data(), e.size() * sizeof(rct::key));
+          memwipe(&skey, sizeof(rct::key));
+        });
+
+        // get local signer's nonces for this transaction attempt's inputs
+        // note: whoever created 'exported_txs' has full power to match proposed tx inputs (selected_transfers)
+        //       with the public nonces of the multisig signers who call this function (via 'used_L' as identifiers), however
+        //       the local signer will only use a given nonce exactly once (even if a used_L is repeated)
+        for (std::size_t i = 0; i < local_nonces_k.size(); ++i) {
+          for (std::size_t j = 0; j < multisig::signing::kAlphaComponents; ++j) {
+            get_multisig_k(sd.selected_transfers[i], sig.used_L, local_nonces_k[i][j]);
+          }
+        }
 
-        for (const auto &msk: get_account().get_multisig_keys())
+        // round-robin signing: sign with all local multisig key shares that other signers have not signed with yet
+        for (const auto &multisig_skey: get_account().get_multisig_keys())
         {
-          crypto::public_key pmsk = get_multisig_signing_public_key(msk);
+          crypto::public_key multisig_pkey = get_multisig_signing_public_key(multisig_skey);
 
-          if (sig.signing_keys.find(pmsk) == sig.signing_keys.end())
+          if (sig.signing_keys.find(multisig_pkey) == sig.signing_keys.end())
           {
-            sc_add(skey.bytes, skey.bytes, rct::sk2rct(msk).bytes);
-            sig.signing_keys.insert(pmsk);
+            sc_add(skey.bytes, skey.bytes, rct::sk2rct(multisig_skey).bytes);
+            sig.signing_keys.insert(multisig_pkey);
           }
         }
-        THROW_WALLET_EXCEPTION_IF(!rct::signMultisig(ptx.tx.rct_signatures, indices, k, sig.msout, skey),
-            error::wallet_internal_error, "Failed signing, transaction likely malformed");
 
-        sig.sigs = ptx.tx.rct_signatures;
+        THROW_WALLET_EXCEPTION_IF(
+          not multisig_tx_builder.next_partial_sign(sig.total_alpha_G, sig.total_alpha_H, local_nonces_k, skey, sig.c_0, sig.s),
+          error::wallet_internal_error,
+          "error: multisig::signing::tx_builder_ringct_t::next_partial_sign"
+        );
       }
     }
 
     const bool is_last = exported_txs.m_signers.size() + 1 >= m_multisig_threshold;
     if (is_last)
     {
-      // when the last signature on a multisig tx is made, we select the right
-      // signature to plug into the final tx
+      // if there are signatures from enough signers (assuming the local signer signed 1+ tx attempts), find the tx
+      //       attempt with a full set of signatures so this tx can be finalized
       bool found = false;
       for (const auto &sig: ptx.multisig_sigs)
       {
         if (sig.ignore.find(local_signer) == sig.ignore.end() && !keys_intersect(sig.ignore, exported_txs.m_signers))
         {
           THROW_WALLET_EXCEPTION_IF(found, error::wallet_internal_error, "More than one transaction is final");
-          ptx.tx.rct_signatures = sig.sigs;
+          THROW_WALLET_EXCEPTION_IF(
+            not multisig_tx_builder.finalize_tx(ptx.construction_data.sources, sig.c_0, sig.s, ptx.tx),
+            error::wallet_internal_error,
+            "error: multisig::signing::tx_builder_ringct_t::finalize_tx"
+          );
           found = true;
         }
       }
       THROW_WALLET_EXCEPTION_IF(!found, error::wallet_internal_error,
-          "Final signed transaction not found: this transaction was likely made without our export data, so we cannot sign it");
+          "Unable to finalize the transaction: the ignore sets for these tx attempts seem to be malformed.");
       const crypto::hash txid = get_transaction_hash(ptx.tx);
       if (store_tx_info())
       {
@@ -7232,7 +7265,8 @@ bool wallet2::sign_multisig_tx(multisig_tx_set &exported_txs, std::vector<crypto
     }
   }
 
-  // txes generated, get rid of used k values
+  // signatures generated, get rid of any unused k values (must do export_multisig() to make more tx attempts with the
+  //   inputs in the transactions worked on here)
   for (size_t n = 0; n < exported_txs.m_ptx.size(); ++n)
     for (size_t idx: exported_txs.m_ptx[n].construction_data.selected_transfers)
       memwipe(m_transfers[idx].m_multisig_k.data(), m_transfers[idx].m_multisig_k.size() * sizeof(m_transfers[idx].m_multisig_k[0]));
@@ -8758,9 +8792,8 @@ void wallet2::transfer_selected(const std::vector<cryptonote::tx_destination_ent
 
   crypto::secret_key tx_key;
   std::vector<crypto::secret_key> additional_tx_keys;
-  rct::multisig_out msout;
   LOG_PRINT_L2("constructing tx");
-  bool r = cryptonote::construct_tx_and_get_tx_key(m_account.get_keys(), m_subaddresses, sources, splitted_dsts, change_dts.addr, extra, tx, unlock_time, tx_key, additional_tx_keys, false, {}, m_multisig ? &msout : NULL, use_view_tags);
+  bool r = cryptonote::construct_tx_and_get_tx_key(m_account.get_keys(), m_subaddresses, sources, splitted_dsts, change_dts.addr, extra, tx, unlock_time, tx_key, additional_tx_keys, false, {}, use_view_tags);
   LOG_PRINT_L2("constructed tx, r="<<r);
   THROW_WALLET_EXCEPTION_IF(!r, error::tx_not_constructed, sources, splitted_dsts, unlock_time, m_nettype);
   THROW_WALLET_EXCEPTION_IF(upper_transaction_weight_limit <= get_transaction_weight(tx), error::tx_too_big, tx, upper_transaction_weight_limit);
@@ -8842,6 +8875,10 @@ void wallet2::transfer_selected_rct(std::vector<cryptonote::tx_destination_entry
 
     // At this step we need to define set of participants available for signature,
     // i.e. those of them who exchanged with multisig info's
+    // note: The oldest unspent owned output's multisig info (in m_transfers) will contain the most recent result of
+    //       'import_multisig()', which means only 'fresh' multisig infos (public nonces) will be used to make tx attempts.
+    //       - If a signer's info was missing from the latest call to 'import_multisig()', then they won't be able to participate!
+    //       - If a newly-acquired output doesn't have enouch nonces from multisig infos, then it can't be spent!
     for (const crypto::public_key &signer: m_multisig_signers)
     {
       if (signer == local_signer)
@@ -8909,7 +8946,6 @@ void wallet2::transfer_selected_rct(std::vector<cryptonote::tx_destination_entry
   LOG_PRINT_L2("preparing outputs");
   size_t i = 0, out_index = 0;
   std::vector<cryptonote::tx_source_entry> sources;
-  std::unordered_set<rct::key> used_L;
   for(size_t idx: selected_transfers)
   {
     sources.resize(sources.size()+1);
@@ -8952,10 +8988,8 @@ void wallet2::transfer_selected_rct(std::vector<cryptonote::tx_destination_entry
     src.real_output_in_tx_index = td.m_internal_output_index;
     src.mask = td.m_mask;
     if (m_multisig)
-    {
-      auto ignore_set = ignore_sets.empty() ? std::unordered_set<crypto::public_key>() : ignore_sets.front();
-      src.multisig_kLRki = get_multisig_composite_kLRki(idx, ignore_set, used_L, used_L);
-    }
+      // note: multisig_kLRki is a legacy struct, currently only used as a key image shuttle into the multisig tx builder
+      src.multisig_kLRki = {.k = {}, .L = {}, .R = {}, .ki = rct::ki2rct(td.m_key_image)};
     else
       src.multisig_kLRki = rct::multisig_kLRki({rct::zero(), rct::zero(), rct::zero(), rct::zero()});
     detail::print_source_entry(src);
@@ -8992,12 +9026,41 @@ void wallet2::transfer_selected_rct(std::vector<cryptonote::tx_destination_entry
 
   crypto::secret_key tx_key;
   std::vector<crypto::secret_key> additional_tx_keys;
-  rct::multisig_out msout;
   LOG_PRINT_L2("constructing tx");
   auto sources_copy = sources;
-  bool r = cryptonote::construct_tx_and_get_tx_key(m_account.get_keys(), m_subaddresses, sources, splitted_dsts, change_dts.addr, extra, tx, unlock_time, tx_key, additional_tx_keys, true, rct_config, m_multisig ? &msout : NULL, use_view_tags);
-  LOG_PRINT_L2("constructed tx, r="<<r);
-  THROW_WALLET_EXCEPTION_IF(!r, error::tx_not_constructed, sources, dsts, unlock_time, m_nettype);
+  multisig::signing::tx_builder_ringct_t multisig_tx_builder;
+  if (m_multisig) {
+    // prepare the core part of a multisig tx (many tx attempts for different signer groups can be spun off this core piece)
+    std::set<std::uint32_t> subaddr_minor_indices;
+    for (size_t idx: selected_transfers) {
+      subaddr_minor_indices.insert(m_transfers[idx].m_subaddr_index.minor);
+    }
+    THROW_WALLET_EXCEPTION_IF(
+      not multisig_tx_builder.init(m_account.get_keys(),
+        extra,
+        unlock_time,
+        subaddr_account,
+        subaddr_minor_indices,
+        sources,
+        splitted_dsts,
+        change_dts,
+        rct_config,
+        true,
+        false,
+        tx_key,
+        additional_tx_keys,
+        tx
+      ),
+      error::wallet_internal_error,
+      "error: multisig::signing::tx_builder_ringct_t::init"
+    );
+  }
+  else {
+    // make a normal tx
+    bool r = cryptonote::construct_tx_and_get_tx_key(m_account.get_keys(), m_subaddresses, sources, splitted_dsts, change_dts.addr, extra, tx, unlock_time, tx_key, additional_tx_keys, true, rct_config, use_view_tags);
+    LOG_PRINT_L2("constructed tx, r="<<r);
+    THROW_WALLET_EXCEPTION_IF(!r, error::tx_not_constructed, sources, dsts, unlock_time, m_nettype);
+  }
   THROW_WALLET_EXCEPTION_IF(upper_transaction_weight_limit <= get_transaction_weight(tx), error::tx_too_big, tx, upper_transaction_weight_limit);
 
   // work out the permutation done on sources
@@ -9015,42 +9078,77 @@ void wallet2::transfer_selected_rct(std::vector<cryptonote::tx_destination_entry
   THROW_WALLET_EXCEPTION_IF(ins_order.size() != sources.size(), error::wallet_internal_error, "Failed to work out sources permutation");
 
   std::vector<tools::wallet2::multisig_sig> multisig_sigs;
-  if (m_multisig)
-  {
-    auto ignore = ignore_sets.empty() ? std::unordered_set<crypto::public_key>() : ignore_sets.front();
-    multisig_sigs.push_back({tx.rct_signatures, ignore, used_L, std::unordered_set<crypto::public_key>(), msout});
-
-    if (m_multisig_threshold < m_multisig_signers.size())
-    {
-      const crypto::hash prefix_hash = cryptonote::get_transaction_prefix_hash(tx);
-
-      // create the other versions, one for every other participant (the first one's already done above)
-      for (size_t ignore_index = 1; ignore_index < ignore_sets.size(); ++ignore_index)
-      {
-        std::unordered_set<rct::key> new_used_L;
-        size_t src_idx = 0;
-        THROW_WALLET_EXCEPTION_IF(selected_transfers.size() != sources.size(), error::wallet_internal_error, "mismatched selected_transfers and sources sixes");
-        for(size_t idx: selected_transfers)
-        {
-          cryptonote::tx_source_entry& src = sources_copy[src_idx];
-          src.multisig_kLRki = get_multisig_composite_kLRki(idx, ignore_sets[ignore_index], used_L, new_used_L);
-          ++src_idx;
+  if (m_multisig) {
+    if (ignore_sets.empty())
+      ignore_sets.emplace_back();
+    const std::size_t num_multisig_attempts = ignore_sets.size();
+    multisig_sigs.resize(num_multisig_attempts);
+    std::unordered_set<rct::key> all_used_L;
+    std::unordered_set<crypto::public_key> signing_keys;
+    for (const crypto::secret_key &multisig_skey: get_account().get_multisig_keys())
+      signing_keys.insert(get_multisig_signing_public_key(multisig_skey));
+    const std::size_t num_sources = sources.size();
+    const std::size_t num_alpha_components = multisig::signing::kAlphaComponents;
+
+    // initiate a multisig tx attempt for each unique set of signers that
+    // a) includes the local signer
+    // b) includes other signers who most recently sent the local signer LR public nonces via 'export_multisig() -> import_multisig()'
+    for (std::size_t i = 0; i < num_multisig_attempts; ++i) {
+      multisig_sig& sig = multisig_sigs[i];
+      sig.total_alpha_G.resize(num_sources, rct::keyV(num_alpha_components));
+      sig.total_alpha_H.resize(num_sources, rct::keyV(num_alpha_components));
+      sig.s.resize(num_sources);
+      sig.c_0.resize(num_sources);
+
+      // for each tx input, get public musig2-style nonces from
+      // a) temporary local-generated private nonces (used to make the local partial signatures on each tx attempt)
+      // b) other signers' public nonces, sent to the local signer via 'export_multisig() -> import_multisig()'
+      // - WARNING: If two multisig players initiate multisig tx attempts separately, but spend the same funds (and hence rely on the same LR public nonces),
+      //            then if two signers partially sign different tx attempt sets, then all attempts that require both signers will become garbage,
+      //            because LR nonces can only be used for one tx attempt.
+      for (std::size_t j = 0; j < num_sources; ++j) {
+        rct::keyV alpha(num_alpha_components);
+        auto alpha_wiper = epee::misc_utils::create_scope_leave_handler([&]{
+          memwipe(static_cast<rct::key *>(alpha.data()), alpha.size() * sizeof(rct::key));
+        });
+        for (std::size_t m = 0; m < num_alpha_components; ++m) {
+          const rct::multisig_kLRki kLRki = get_multisig_composite_kLRki(
+            selected_transfers[ins_order[j]],
+            ignore_sets[i],
+            all_used_L,  //collect all public L nonces used by this tx proposal (set of tx attempts) to avoid duplicates
+            sig.used_L   //record the public L nonces used by this tx input to this tx attempt, for coordination with other signers
+          );
+          alpha[m] = kLRki.k;
+          sig.total_alpha_G[j][m] = kLRki.L;
+          sig.total_alpha_H[j][m] = kLRki.R;
         }
 
-        LOG_PRINT_L2("Creating supplementary multisig transaction");
-        cryptonote::transaction ms_tx;
-        auto sources_copy_copy = sources_copy;
-        bool shuffle_outs = false;
-        bool r = cryptonote::construct_tx_with_tx_key(m_account.get_keys(), m_subaddresses, sources_copy_copy, splitted_dsts, change_dts.addr, extra, ms_tx, unlock_time,tx_key, additional_tx_keys, true, rct_config, &msout, shuffle_outs, use_view_tags);
-        LOG_PRINT_L2("constructed tx, r="<<r);
-        THROW_WALLET_EXCEPTION_IF(!r, error::tx_not_constructed, sources, splitted_dsts, unlock_time, m_nettype);
-        THROW_WALLET_EXCEPTION_IF(upper_transaction_weight_limit <= get_transaction_weight(tx), error::tx_too_big, tx, upper_transaction_weight_limit);
-        THROW_WALLET_EXCEPTION_IF(cryptonote::get_transaction_prefix_hash(ms_tx) != prefix_hash, error::wallet_internal_error, "Multisig txes do not share prefix");
-        multisig_sigs.push_back({ms_tx.rct_signatures, ignore_sets[ignore_index], new_used_L, std::unordered_set<crypto::public_key>(), msout});
-
-        ms_tx.rct_signatures = tx.rct_signatures;
-        THROW_WALLET_EXCEPTION_IF(cryptonote::get_transaction_hash(ms_tx) != cryptonote::get_transaction_hash(tx), error::wallet_internal_error, "Multisig txes differ by more than the signatures");
-      }
+        // local signer: initial partial signature on this tx input for this tx attempt
+        // note: sign here with sender-receiver secret component, subaddress component, and ALL of the local signer's multisig key shares
+        //       (this ultimately occurs deep in generate_key_image_helper_precomp())
+        THROW_WALLET_EXCEPTION_IF(
+          not multisig_tx_builder.first_partial_sign(j, sig.total_alpha_G[j], sig.total_alpha_H[j], alpha, sig.c_0[j], sig.s[j]),
+          error::wallet_internal_error,
+          "error: multisig::signing::tx_builder_ringct_t::first_partial_sign"
+        );
+      }
+
+      // note: record the ignore set so when other signers go to add their signatures (sign_multisig_tx()), they
+      //       can skip this tx attempt if they aren't supposed to sign it; this only works for signers who provided
+      //       multisig_infos to the last 'import_multisig()' call by the local signer, all 'other signers' will encounter
+      //       a 'need to export multisig_info' wallet error if they try to sign this partial tx, which means if they want to sign a tx
+      //       they need to export_multisig() -> send to the local signer -> local signer calls import_multisig() with fresh
+      //       multisig_infos from all signers -> local signer makes completely new tx attempts (or a different signer makes tx attempts)
+      sig.ignore = ignore_sets[i];
+      sig.signing_keys = signing_keys;  //the local signer signed with ALL of their multisig key shares, record their pubkeys for reference by other signers
+    }
+    if (m_multisig_threshold <= 1) {
+      // local signer: finish signing the tx inputs if we are the only signer (ignore all but the first 'attempt')
+      THROW_WALLET_EXCEPTION_IF(
+        not multisig_tx_builder.finalize_tx(sources, multisig_sigs[0].c_0, multisig_sigs[0].s, tx),
+        error::wallet_internal_error,
+        "error: multisig::signing::tx_builder_ringct_t::finalize_tx"
+      );
     }
   }
 
@@ -13336,19 +13434,26 @@ crypto::public_key wallet2::get_multisig_signing_public_key(size_t idx) const
   return get_multisig_signing_public_key(get_account().get_multisig_keys()[idx]);
 }
 //----------------------------------------------------------------------------------------------------
-rct::key wallet2::get_multisig_k(size_t idx, const std::unordered_set<rct::key> &used_L) const
+void wallet2::get_multisig_k(size_t idx, const std::unordered_set<rct::key> &used_L, rct::key &nonce)
 {
   CHECK_AND_ASSERT_THROW_MES(m_multisig, "Wallet is not multisig");
   CHECK_AND_ASSERT_THROW_MES(idx < m_transfers.size(), "idx out of range");
-  for (const auto &k: m_transfers[idx].m_multisig_k)
+  for (auto &k: m_transfers[idx].m_multisig_k)
   {
+    if (k == rct::zero())
+      continue;
+
+    // decide whether or not to return a nonce just based on if its pubkey 'L = k*G' is attached to the transfer 'idx'
     rct::key L;
     rct::scalarmultBase(L, k);
     if (used_L.find(L) != used_L.end())
-      return k;
+    {
+      nonce = k;
+      memwipe(static_cast<rct::key *>(&k), sizeof(rct::key));  //CRITICAL: a nonce may only be used once!
+      return;
+    }
   }
   THROW_WALLET_EXCEPTION(tools::error::multisig_export_needed);
-  return rct::zero();
 }
 //----------------------------------------------------------------------------------------------------
 rct::multisig_kLRki wallet2::get_multisig_kLRki(size_t n, const rct::key &k) const
@@ -13414,15 +13519,23 @@ cryptonote::blobdata wallet2::export_multisig()
 
   const crypto::public_key signer = get_multisig_signer_public_key();
 
+  // For each transfer (output owned by the multisig wallet):
+  // 1) Record the output's partial key image (from the local signer), so other signers can assemble the output's full key image.
+  // 2) Prepare enough signing nonces for one signing attempt with each possible combination of 'threshold' signers
+  //    from the multisig group (only groups that include the local signer).
+  //    - Calling this function will reset any nonces recorded by the previous call to this function. Doing so will
+  //      invalidate any in-progress signing attempts that rely on the previous output of this function.
   info.resize(m_transfers.size());
   for (size_t n = 0; n < m_transfers.size(); ++n)
   {
     transfer_details &td = m_transfers[n];
     crypto::key_image ki;
-    memwipe(td.m_multisig_k.data(), td.m_multisig_k.size() * sizeof(td.m_multisig_k[0]));
+    if (td.m_multisig_k.size())
+      memwipe(td.m_multisig_k.data(), td.m_multisig_k.size() * sizeof(td.m_multisig_k[0]));
     info[n].m_LR.clear();
     info[n].m_partial_key_images.clear();
 
+    // record the partial key images
     for (size_t m = 0; m < get_account().get_multisig_keys().size(); ++m)
     {
       // we want to export the partial key image, not the full one, so we can't use td.m_key_image
@@ -13435,6 +13548,15 @@ cryptonote::blobdata wallet2::export_multisig()
     // if we have 2/4 wallet with signers: A, B, C, D and A is a transaction creator it will need to pick up 1 signer from 3 wallets left.
     // That means counting combinations for excluding 2-of-3 wallets (k = total signers count - threshold, n = total signers count - 1).
     size_t nlr = tools::combinations_count(m_multisig_signers.size() - m_multisig_threshold, m_multisig_signers.size() - 1);
+
+    // 'td.m_multisig_k' is an expansion of [{alpha_0, alpha_1, ...}, {alpha_0, alpha_1, ...}, {alpha_0, alpha_1, ...}],
+    //    - A '{alpha_0, alpha_1, ...}' tuple contains a set of 'kAlphaComponents' nonces, which can be used for one
+    //      signing attempt. Each output will gain 'nlr' tuples, so that every signing group can make one signing attempt.
+    //    - All tuples are always cleared after 1+ of them is used to sign a tx attempt (in sign_multisig_tx()), so
+    //      in practice, a call to this function only allows _one_ multisig signing cycle for each output (which can
+    //      include signing attempts for multiple signer groups).
+    nlr *= multisig::signing::kAlphaComponents;
+
     for (size_t m = 0; m < nlr; ++m)
     {
       td.m_multisig_k.push_back(rct::skGen());
```
