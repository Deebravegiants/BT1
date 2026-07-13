I have traced the full code path. Here is my analysis:

**Trace:**

1. `blob_to_key` in `src/cbmpc/api/eddsa2pc.cpp` validates `x_share` with `q.is_in_range(blob.x_share)`. The implementation is `bool mod_t::is_in_range(const bn_t& a) const { return a.sign() >= 0 && a < m; }` — so `is_in_range(0)` returns **true** (0 ≥ 0 and 0 < q). A crafted blob with `x_share = 0` passes deserialization. [1](#0-0) [2](#0-1) 

2. `get_public_share_compressed` then computes `x = key.x_share % q = 0`, then `(0 * G).to_compressed_bin()`. There is no check for `x == 0` or for the resulting point being infinity. [3](#0-2) 

3. `ec25519_core::to_bin` explicitly handles the infinity case by writing `{0x01, 0x00, ..., 0x00}` (32 bytes) and returning — no error. So `get_public_share_compressed` returns **SUCCESS** with a 32-byte identity-point encoding. [4](#0-3) 

4. In `attach_private_scalar`, the identity encoding `{0x01, 0x00...}` is parsed by `from_bin` as the Edwards point (x=0, y=1), which is the identity element. `curve.check(Qi_self)` passes because (0,1) satisfies the Edwards equation `-x²+y²=1+dx²y²` → `1=1`. `is_in_subgroup` passes because `(q-1)·O = O = -O`, so `O == -O` is true. `is_in_range(0)` passes. Finally, `0 * G == identity == Qi_self` so the consistency check passes. `attach_private_scalar` returns **SUCCESS**. [5](#0-4) [6](#0-5) 

**Conclusion:**

The described path is real and reachable:
- `get_public_share_compressed` with a crafted `x_share=0` blob returns `SUCCESS` + identity encoding.
- `attach_private_scalar` with a zero scalar + identity encoding returns `SUCCESS`.

Both are concrete accepted-bad-output paths. However, the **security impact** is bounded: an attacker who controls their own key blob can already manipulate it arbitrarily. The zero-scalar blob does not by itself allow forging a signature without the honest peer's participation in the interactive signing protocol — the 2-party signing protocol still requires both parties. The impact is a **validation bypass** (High per the defined scope): the public API accepts a zero scalar and the identity point as a valid key share pair, violating the invariant that key shares must be non-zero non-identity points.

---

### Title
`get_public_share_compressed` accepts zero scalar and returns identity-point encoding as valid public share — (`src/cbmpc/api/eddsa2pc.cpp`)

### Summary
`get_public_share_compressed` does not reject `x_share = 0`. Because `is_in_range(0)` returns true (0 is in `[0, q)`), a crafted blob with `x_share = 0` passes deserialization. The function then computes `0 * G = identity` and serializes it without error. The resulting 32-byte identity encoding subsequently passes all checks in `attach_private_scalar` (on-curve, subgroup, scalar-range, and `x*G == Qi` consistency), allowing a zero scalar to be round-tripped through the detach/attach API as a valid key share.

### Finding Description
In `src/cbmpc/api/eddsa2pc.cpp`, `blob_to_key` validates `x_share` only with `q.is_in_range(blob.x_share)`, which accepts 0. `get_public_share_compressed` then computes `(0 % q) * G = identity` and calls `to_compressed_bin()` on it. `ec25519_core::to_bin` handles the infinity case by writing `{0x01, 0x00×31}` and returning without error. No guard checks whether the resulting point is the identity before returning SUCCESS.

In `attach_private_scalar`, the identity encoding is accepted because: (a) `from_bin` successfully parses (0,1); (b) `curve.check` passes since (0,1) satisfies the Edwards equation; (c) `is_in_subgroup` returns true since `(q-1)·O = O = -O`; (d) `is_in_range(0)` returns true; (e) `0*G == identity` satisfies the consistency check.

### Impact Explanation
The public API accepts a zero scalar as a valid private key share and the identity point as its corresponding public share. This violates the fundamental invariant that key shares must be non-zero. A party holding a zero share contributes nothing to the combined key, meaning the other party's share alone constitutes the full private key. Any downstream system (e.g., PVE) that relies on `get_public_share_compressed` output being a valid non-identity point will receive silently incorrect data.

### Likelihood Explanation
Requires an attacker who can supply a crafted key blob to the API (e.g., a malicious blob provider or a party that tampers with their own stored blob). The crafted blob is trivially constructable by serializing a `key_blob_v1_t` with `x_share = 0`.

### Recommendation
In `blob_to_key`, add an explicit non-zero check after the range check:
```cpp
if (!q.is_in_range(blob.x_share)) return coinbase::error(E_FORMAT, "invalid key blob");
if (blob.x_share == 0) return coinbase::error(E_FORMAT, "invalid key blob: zero scalar");
```
In `get_public_share_compressed`, after computing the point, add:
```cpp
if (curve.is_infinity(result_point)) return coinbase::error(E_FORMAT, "invalid key blob: zero scalar");
```

### Proof of Concept
```cpp
// Craft a blob with x_share = 0
key_blob_v1_t bad_blob;
bad_blob.version = 1;
bad_blob.role = 0;
bad_blob.curve = static_cast<uint32_t>(curve_id::ed25519);
bad_blob.Q_compressed = /* any valid Q */;
bad_blob.x_share = 0;  // zero scalar
buf_t bad_blob_bytes = coinbase::convert(bad_blob);

buf_t Qi;
error_t rv = coinbase::api::eddsa_2p::get_public_share_compressed(bad_blob_bytes, Qi);
// rv == SUCCESS, Qi == {0x01, 0x00, ..., 0x00} (identity encoding)
assert(rv == SUCCESS);  // should be E_FORMAT

// Also verify attach_private_scalar accepts it
buf_t pub_blob, x_fixed;
coinbase::api::eddsa_2p::detach_private_scalar(bad_blob_bytes, pub_blob, x_fixed);
// x_fixed == {0x00 × 32}
buf_t merged;
rv = coinbase::api::eddsa_2p::attach_private_scalar(pub_blob, x_fixed, Qi, merged);
assert(rv == SUCCESS);  // should be E_FORMAT
```

### Citations

**File:** src/cbmpc/api/eddsa2pc.cpp (L36-38)
```cpp
  const coinbase::crypto::mod_t& q = key.curve.order();
  if (!q.is_in_range(blob.x_share)) return coinbase::error(E_FORMAT, "invalid key blob");
  key.x_share = blob.x_share;
```

**File:** src/cbmpc/api/eddsa2pc.cpp (L134-148)
```cpp
error_t get_public_share_compressed(mem_t key_blob, buf_t& out_public_share_compressed) {
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(key_blob, "key_blob",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  coinbase::mpc::eddsa2pc::key_t key;
  error_t rv = deserialize_key_blob(key_blob, key);
  if (rv) return rv;

  const auto curve = coinbase::crypto::curve_ed25519;
  const coinbase::crypto::mod_t& q = curve.order();
  const auto& G = curve.generator();
  const coinbase::crypto::bn_t x = key.x_share % q;
  out_public_share_compressed = (x * G).to_compressed_bin();
  return SUCCESS;
}
```

**File:** src/cbmpc/api/eddsa2pc.cpp (L201-211)
```cpp
  coinbase::crypto::ecc_point_t Qi_self(curve);
  if (rv = Qi_self.from_bin(curve, public_share_compressed))
    return coinbase::error(rv, "invalid public_share_compressed");
  if (rv = curve.check(Qi_self)) return coinbase::error(rv, "invalid public_share_compressed");
  if (!Qi_self.is_in_subgroup()) return coinbase::error(E_FORMAT, "invalid public_share_compressed");

  const coinbase::crypto::bn_t x = coinbase::crypto::bn_t::from_bin(private_scalar_fixed) % q;
  if (!q.is_in_range(x)) return coinbase::error(E_FORMAT, "invalid private_scalar_fixed");

  const auto& G = curve.generator();
  if (x * G != Qi_self) return coinbase::error(E_FORMAT, "x_share mismatch key blob");
```

**File:** src/cbmpc/crypto/base_mod.cpp (L88-88)
```cpp
bool mod_t::is_in_range(const bn_t& a) const { return a.sign() >= 0 && a < m; }
```

**File:** src/cbmpc/crypto/ec25519_core.cpp (L865-870)
```cpp
bool is_in_subgroup(const crypto::ecp_storage_t* a) {
  static bn_t q_minus_1 = bn_t::from_hex("1000000000000000000000000000000014DEF9DEA2F79CD65812631A5CF5D3EC");
  point_t x;
  curve_t::mul(*(const point_t*)a, q_minus_1, x);
  return *(const point_t*)a == -x;
}
```

**File:** src/cbmpc/crypto/ec25519_core.cpp (L916-928)
```cpp
static void to_bin(const point_t& P, byte_ptr r) {
  if (P.is_infinity()) {
    r[0] = 1;
    memset(r + 1, 0, 31);
    return;
  }

  fe_t x, y;
  P.get_xy(x, y);
  y.from_fe().to_bin(r);
  mem_t(r, 32).reverse();
  r[31] ^= int(x.is_odd()) << 7;
}
```
