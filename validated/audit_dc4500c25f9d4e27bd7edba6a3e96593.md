Looking at the bug class: **position-indexed lookup into a data structure built with a different ordering than the one used at lookup time**, combined with an early-exit algorithm that assumes sorted order.

I traced the most structurally analogous pattern in cb-mpc: the `ec_pve_ac_t` PVE-AC system, which uses a position-indexed `quorum_c` vector.

**Encryption side** (`encrypt_row` in `src/cbmpc/protocol/pve_ac.cpp`): [1](#0-0) 

`quorum_c` is built by iterating over `ac_pks` (`std::map<std::string, pve_keyref_t>`), which iterates in **lexicographic order of keys**.

**Decryption side** (`party_decrypt_row`): [2](#0-1) 

`sorted_leaves` is built from `ac.list_leaf_names()` → `std::set<pname_t>` → vector, also in **lexicographic order of leaf names**.

**Lookup** (`find_quorum_ciphertext`): [3](#0-2) 

Both sides use the same lexicographic ordering of the same leaf names, and `validate_leaf_keys_exact` enforces that `ac_pks` keys match the access structure leaf names exactly:
<cite repo="Tylerpinwa/cb-

### Citations

**File:** src/cbmpc/protocol/pve_ac.cpp (L32-38)
```cpp
  for (const auto& [path, pub_key_ptr] : ac_pks) {
    ciphertext_adapter_t item;
    buf_t ct_ser;
    if (rv = base_pke.encrypt(pub_key_ptr, L, K_shares[path].to_bin(), drbg.gen(32), ct_ser)) return rv;
    item.ct_ser = ct_ser;
    quorum_c.push_back(std::move(item));
  }
```

**File:** src/cbmpc/protocol/pve_ac.cpp (L195-205)
```cpp
error_t ec_pve_ac_t::find_quorum_ciphertext(const std::vector<std::string>& sorted_leaves, const std::string& path,
                                            const row_t& row, const ciphertext_adapter_t*& c) {
  auto it = std::find(sorted_leaves.begin(), sorted_leaves.end(), path);
  if (it == sorted_leaves.end()) return coinbase::error(E_NOT_FOUND, "path not found");
  auto index = it - sorted_leaves.begin();

  const auto& quorum_c = row.quorum_c;
  if (index >= quorum_c.size()) return coinbase::error(E_NOT_FOUND, "path not found");
  c = &quorum_c[index];

  return SUCCESS;
```

**File:** src/cbmpc/protocol/pve_ac.cpp (L219-223)
```cpp
  std::set<std::string> leaves = ac.list_leaf_names();
  std::vector<std::string> sorted_leaves(leaves.begin(), leaves.end());

  const ciphertext_adapter_t* c;
  if (rv = find_quorum_ciphertext(sorted_leaves, path, row, c)) return rv;
```
