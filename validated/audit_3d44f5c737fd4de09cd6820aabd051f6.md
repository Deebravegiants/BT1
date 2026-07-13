### Title
Wrong Index Collection in PVE-AC Ciphertext Lookup Breaks Recovery When `ac_pks` Is a Proper Subset of AC Leaves — (`src/cbmpc/protocol/pve_ac.cpp`)

---

### Summary

`ec_pve_ac_t::find_quorum_ciphertext` computes a lookup index using the position of a leaf path inside **all** AC leaf names (`ac.list_leaf_names()`), but uses that index to address `row.quorum_c`, which was built by iterating only the keys present in `ac_pks` during `encrypt()`. When `ac_pks` is a proper subset of the AC's leaves — a valid and documented use-case for threshold structures — the two orderings diverge, so every party whose leaf name is not the first alphabetically in `ac_pks` either receives the wrong ciphertext or an out-of-bounds `E_NOT_FOUND`, making PVE recovery impossible.

---

### Finding Description

**Encryption side** (`encrypt_row`, called from `encrypt`):

`quorum_c` is populated by iterating `ac_pks`, a `std::map<std::string, pve_keyref_t>` that iterates in sorted key order:

```cpp
for (const auto& [path, pub_key_ptr] : ac_pks) {
    ...
    quorum_c.push_back(std::move(item));   // position = rank within ac_pks
}
``` [1](#0-0) 

So `quorum_c[0]` holds the ciphertext for the alphabetically-first key in `ac_pks`, `quorum_c[1]` for the second, and so on.

**Decryption side** (`party_decrypt_row` → `find_quorum_ciphertext`):

`sorted_leaves` is built from **all** AC leaf names, not from `ac_pks`:

```cpp
std::set<std::string> leaves = ac.list_leaf_names();
std::vector<std::string> sorted_leaves(leaves.begin(), leaves.end());
...
if (rv = find_quorum_ciphertext(sorted_leaves, path, row, c)) return rv;
``` [2](#0-1) 

Inside `find_quorum_ciphertext`, the index of `path` in `sorted_leaves` (rank among **all** AC leaves) is used to address `quorum_c` (rank among **ac_pks** leaves only):

```cpp
auto index = it - sorted_leaves.begin();   // rank in ALL ac leaves
...
c = &quorum_c[index];                      // but quorum_c is indexed by rank in ac_pks
``` [3](#0-2) 

**Concrete mismatch example:**

| AC leaves (sorted) | ac_pks (subset) | quorum_c index | sorted_leaves index |
|---|---|---|---|
| alice | — | — | 0 |
| bob | bob → key_b | 0 | 1 |
| charlie | charlie → key_c | 1 | 2 |

- `party_decrypt_row("bob")` → `index=1` → `quorum_c[1]` = charlie's ciphertext → decryption with bob's key fails.
- `party_decrypt_row("charlie")` → `index=2` → `quorum_c.size()==2` → `E_NOT_FOUND`.

Recovery is impossible even though a valid quorum was supplied.

---

### Impact Explanation

`ec_pve_ac_t` is the access-structure PVE primitive used for key-backup workflows. When a threshold quorum attempts to recover a backed-up key share via `party_decrypt_row` + `aggregate_to_restore_row`, every party whose leaf name is not the alphabetically-first entry in `ac_pks` either receives the wrong ciphertext (causing a PKE decryption failure) or an explicit `E_NOT_FOUND`. The aggregation step therefore never receives a valid quorum of decrypted shares, and the secret is permanently unrecoverable. This violates the recovery/liveness invariant of the PVE scheme.

---

### Likelihood Explanation

The trigger condition — `ac_pks` being a proper subset of `ac.list_leaf_names()` — is the normal operating mode for any threshold (t-of-n, n > t) access structure where only the t participating parties' keys are supplied at encryption time. Any caller that encrypts for a strict quorum (rather than all n parties) will hit this bug on the first recovery attempt.

---

### Recommendation

Replace the `sorted_leaves` source in `party_decrypt_row` with the sorted keys of `ac_pks` (i.e., the same ordering used during `encrypt_row`), or store the leaf path alongside each `ciphertext_adapter_t` so that `find_quorum_ciphertext` can perform a name-keyed lookup instead of a positional one. Add a regression test that: (1) creates a 2-of-3 AC, (2) encrypts with only the two non-first-alphabetical parties' keys, (3) calls `party_decrypt_row` for each, and (4) verifies that `aggregate_to_restore_row` succeeds.

---

### Proof of Concept

```
AC leaves (sorted): alice, bob, charlie
ac_pks supplied to encrypt(): { bob → pk_bob, charlie → pk_charlie }

After encrypt_row():
  quorum_c = [ Enc(pk_bob, K_share_bob),      // index 0
               Enc(pk_charlie, K_share_charlie) // index 1 ]

party_decrypt_row(path="bob"):
  sorted_leaves = ["alice","bob","charlie"]
  index of "bob" = 1
  → returns quorum_c[1] = Enc(pk_charlie, K_share_charlie)
  → base_pke.decrypt(sk_bob, ...) fails (wrong key)

party_decrypt_row(path="charlie"):
  index of "charlie" = 2
  quorum_c.size() = 2  →  2 >= 2  →  E_NOT_FOUND

aggregate_to_restore_row() never receives valid shares → recovery fails.
``` [4](#0-3) [5](#0-4) [1](#0-0)

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

**File:** src/cbmpc/protocol/pve_ac.cpp (L195-206)
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
}
```

**File:** src/cbmpc/protocol/pve_ac.cpp (L208-228)
```cpp
error_t ec_pve_ac_t::party_decrypt_row(const pve_base_pke_i& base_pke, const ss::ac_t& ac, int row_index,
                                       const std::string& path, pve_keyref_t prv_key, mem_t label,
                                       bn_t& out_share) const {
  error_t rv = UNINITIALIZED_ERROR;
  if (row_index < 0 || row_index >= kappa) return coinbase::error(E_RANGE);
  if (Q.empty()) return coinbase::error(E_BADARG);

  const row_t& row = rows[row_index];

  buf_t L = crypto::sha256_t::hash(label, Q);

  std::set<std::string> leaves = ac.list_leaf_names();
  std::vector<std::string> sorted_leaves(leaves.begin(), leaves.end());

  const ciphertext_adapter_t* c;
  if (rv = find_quorum_ciphertext(sorted_leaves, path, row, c)) return rv;

  buf_t plain;
  if (rv = base_pke.decrypt(prv_key, L, c->ct_ser, plain)) return rv;
  out_share = bn_t::from_bin(plain);
  return SUCCESS;
```
