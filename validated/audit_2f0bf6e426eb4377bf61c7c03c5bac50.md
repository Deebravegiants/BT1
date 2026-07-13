The key is understanding exactly which `convert` overload is called and whether it checks for trailing bytes. Let me verify the two distinct overloads.

The analysis is complete. Here is the finding:

---

### Title
Trailing-Byte Acceptance in `pve_ciphertext_blob_v1_t` Deserialization Enables Ciphertext Malleability - (`src/cbmpc/api/pve_base_pke.cpp`)

### Summary
All public PVE API functions (`decrypt`, `verify`, `get_public_key_compressed`, `get_Label`) deserialize the outer ciphertext blob using `coinbase::convert(blob, ciphertext)`. This template overload does **not** check for trailing bytes after deserialization. An attacker can append arbitrary bytes to any valid ciphertext and have it accepted as equivalent to the original by every API function.

### Finding Description

The codebase provides two distinct deserialization paths:

**`deser()` — strict, rejects trailing bytes:** [1](#0-0) 

**`convert(T& dst, mem_t src)` — lenient, no trailing-byte check:** [2](#0-1) 

Every public API entry point uses the lenient `convert()` overload: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

The outer blob structure is: [7](#0-6) 

When deserializing, `buf_t::convert` reads a length-prefixed buffer — it reads exactly `value_size` bytes into `blob.ct` and advances the offset by that amount: [8](#0-7) 

Any bytes appended after the valid encoding are left unconsumed in the `converter_t`. Since `coinbase::convert()` only calls `converter.get_rv()` and never checks `converter.get_offset() != converter.get_size()`, it returns `SUCCESS`. The trailing bytes are silently discarded. `blob.ct` contains exactly the original inner ciphertext bytes, so the subsequent `coinbase::convert(pve_ct, blob.ct)` also succeeds and all cryptographic operations proceed identically to the original.

### Impact Explanation

This breaks the non-malleability of the ciphertext format at the API boundary. Two distinct byte sequences — the original ciphertext and any number of variants with arbitrary bytes appended — are accepted as identical by `decrypt`, `verify`, `get_public_key_compressed`, and `get_Label`. Any application that:
- uses the raw ciphertext bytes as a canonical identifier (deduplication, replay protection, audit log),
- stores or compares ciphertext blobs for integrity checking, or
- relies on the library to reject non-canonical encodings

will silently accept forged/mutated blobs as valid. The `verify()` function in particular is expected to authenticate a ciphertext; accepting a mutated form undermines that guarantee.

### Likelihood Explanation

The attack requires only the ability to submit a ciphertext to any of the public API functions — the minimum attacker capability assumed by the scope. No key material, threshold collusion, or privileged access is needed. The mutation is trivially constructible (append any bytes to a legitimately obtained ciphertext).

### Recommendation

Replace `coinbase::convert(blob, ciphertext)` with `coinbase::deser(ciphertext, blob)` at every API entry point that deserializes `pve_ciphertext_blob_v1_t`. The `deser()` function already implements the correct strict check: [9](#0-8) 

The same fix should be applied to the inner `coinbase::convert(pve_ct, blob.ct)` call (replace with `deser`) to enforce strictness at both deserialization layers.

### Proof of Concept

```
1. Obtain a valid ciphertext blob C from encrypt().
2. Construct C' = C || [0xDE, 0xAD, 0xBE, 0xEF, ...] (16 arbitrary bytes appended).
3. Call verify(curve, ek, C', Q_compressed, label)  → returns same result as verify(..., C, ...).
4. Call decrypt(curve, dk, ek, C', label, out_x)    → returns same result as decrypt(..., C, ...).
5. Call get_public_key_compressed(C', out_Q)         → returns same Q as for C.
```

All three calls succeed and return identical outputs for `C` and `C'`, confirming that the trailing bytes are silently ignored and the modified ciphertext is fully accepted.

### Citations

**File:** include-internal/cbmpc/internal/core/convert.h (L253-266)
```text
template <typename... ARGS>
error_t deser(mem_t bin, ARGS&... args) {
  converter_t converter(bin);
  converter.convert(args...);
  error_t rv = converter.get_rv();
  if (rv != SUCCESS) return rv;

  // Strict deserialization: reject trailing bytes
  if (converter.get_offset() != converter.get_size()) {
    return coinbase::error(E_BADARG);
  }

  return SUCCESS;
}
```

**File:** include-internal/cbmpc/internal/core/convert.h (L276-282)
```text
template <typename T>
error_t convert(T& dst, mem_t src) {
  if (src.size < 0 || (src.size && !src.data)) return coinbase::error(E_BADARG);
  converter_t converter(src);
  converter.convert(dst);
  return converter.get_rv();
}
```

**File:** src/cbmpc/api/pve_base_pke.cpp (L19-24)
```cpp
struct pve_ciphertext_blob_v1_t {
  uint32_t version = pve_ciphertext_version_v1;
  buf_t ct;  // serialized `coinbase::mpc::ec_pve_t`

  void convert(coinbase::converter_t& c) { c.convert(version, ct); }
};
```

**File:** src/cbmpc/api/pve_base_pke.cpp (L225-227)
```cpp
  pve_ciphertext_blob_v1_t blob;
  if (rv = coinbase::convert(blob, ciphertext)) return rv;
  if (blob.version != pve_ciphertext_version_v1) return coinbase::error(E_FORMAT, "unsupported ciphertext version");
```

**File:** src/cbmpc/api/pve_base_pke.cpp (L264-266)
```cpp
  pve_ciphertext_blob_v1_t blob;
  if (rv = coinbase::convert(blob, ciphertext)) return rv;
  if (blob.version != pve_ciphertext_version_v1) return coinbase::error(E_FORMAT, "unsupported ciphertext version");
```

**File:** src/cbmpc/api/pve_base_pke.cpp (L345-347)
```cpp
  pve_ciphertext_blob_v1_t blob;
  if (rv = coinbase::convert(blob, ciphertext)) return rv;
  if (blob.version != pve_ciphertext_version_v1) return coinbase::error(E_FORMAT, "unsupported ciphertext version");
```

**File:** src/cbmpc/api/pve_base_pke.cpp (L362-364)
```cpp
  pve_ciphertext_blob_v1_t blob;
  if (rv = coinbase::convert(blob, ciphertext)) return rv;
  if (blob.version != pve_ciphertext_version_v1) return coinbase::error(E_FORMAT, "unsupported ciphertext version");
```

**File:** src/cbmpc/core/buf.cpp (L305-324)
```cpp
void buf_t::convert(converter_t& converter) {
  uint32_t value_size = size();
  converter.convert_len(value_size);

  if (converter.is_write()) {
    if (!converter.is_calc_size()) memmove(converter.current(), data(), value_size);
  } else {
    if (int(value_size) < 0) {
      converter.set_error();
      return;
    }  // deserialization length validation

    if (converter.is_error() || !converter.at_least(value_size)) {
      converter.set_error();
      return;
    }
    memmove(alloc(value_size), converter.current(), value_size);
  }
  converter.forward(value_size);
}
```
