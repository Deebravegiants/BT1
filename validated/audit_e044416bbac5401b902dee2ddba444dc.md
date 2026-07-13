### Title
Mode-Confusion via Empty `w0` in `ot_ext_protocol_ctx_t::output_R` Causes Receiver to Accept Wrong OT Outputs — (`src/cbmpc/protocol/ot.cpp`)

---

### Summary

`ot_ext_protocol_ctx_t::output_R` infers the protocol variant from the runtime emptiness of the deserialized `w0` field. A malicious sender can craft a `msg3` with an empty `w0` vector and a valid `w1` vector, forcing the receiver into `sender_one_input_random_mode` even though it ran the Full-OT-2P path. The receiver then computes wrong OT outputs for all choice bits `r[i] = 0` and returns `SUCCESS`, silently accepting attacker-controlled values.

---

### Finding Description

**Mode determination is data-driven, not state-driven.**

In `ot_ext_protocol_ctx_t::output_R`:

```cpp
bool sender_one_input_random_mode = w0.empty();   // line 359
if (!sender_one_input_random_mode) {
    if (m != int(w0.size())) return coinbase::error(E_FORMAT);
}
if (m != int(w1.size())) return coinbase::error(E_FORMAT);
``` [1](#0-0) 

The mode flag is derived entirely from whether `w0` is empty after deserialization. There is no stored state from `step1_R2S` that records which variant the receiver committed to.

**The sender controls `w0` via `msg3`.**

`ot_protocol_pvw_ctx_t::msg3()` returns `ext.msg2()`, which is `std::tie(w0, w1)`: [2](#0-1) [3](#0-2) 

The `converter_t` framework deserializes `std::vector<buf_t>` by reading a length-prefixed count. A sender that writes count=0 for `w0` and count=`m` for `w1` produces a valid wire encoding that passes all `converter_t` checks (no negative-count rejection, no minimum-size enforcement).

**Attack trace:**

1. Honest receiver runs `step2_R2S(r, l)` → `ext.step1_R2S(...)` → sets up `T`, `r`, `l`, `U`, `v0`, `v1`.
2. Malicious sender crafts `msg3`: serializes `w0` with count=0, `w1` with `m` entries of the correct byte-length `bits_to_bytes(l)`.
3. Receiver deserializes: `ext.w0 = {}`, `ext.w1 = [m valid entries]`.
4. Receiver calls `output_R(m, x)`:
   - `sender_one_input_random_mode = true` (because `w0.empty()`)
   - `m != int(w0.size())` check is **skipped**
   - `m != int(w1.size())` passes
   - For each `i`: `x[i] = hash_matrix_line(i, T[i], l) ^ ct_select(r[i], w1[i], w_zero)`
5. Returns `SUCCESS`.

**What the receiver actually computes vs. what it should:**

| `r[i]` | Honest output | Attack output |
|--------|--------------|---------------|
| 0 | `hash(T[i]) ^ w0[i] = x0[i]` | `hash(T[i]) ^ 0 = hash(T[i])` ≠ `x0[i]` |
| 1 | `hash(T[i]) ^ w1[i] = x1[i]` | `hash(T[i]) ^ w1[i]` (sender-controlled) | [4](#0-3) 

For all `i` where `r[i] = 0`, the receiver obtains `hash(T[i])` — a value the sender can predict (since the sender knows `Q[i]` and the OT extension property gives `T[i] = Q[i]` when `r[i] = 0`). The sender can therefore set `w1[i]` to any value and fully control the receiver's output for `r[i] = 1` bits as well.

**No guard exists.** The honest sender path (`step2_S2R_helper` with `sender_one_input_random_mode = false`) always sets `w0.resize(m)` before returning: [5](#0-4) 

But this resize happens on the **sender's** context object, not the receiver's. The receiver's `w0` is populated only by deserialization of the incoming message.

---

### Impact Explanation

OT is used directly in ECDSA multi-party signing. The receiver's OT output `X_bin` feeds the Gilboa multiplication: [6](#0-5) 

With attacker-controlled OT outputs, the multiplication result is wrong for all choice bits `r[i] = 0`. Since the choice bits encode bits of a secret scalar (e.g., `k_i` or `x_i`), the sender can:

- Predict the receiver's output for `r[i] = 0` positions (it equals `hash(Q[i])`).
- Observe the final protocol output (e.g., a signature) and correlate it with the injected wrong values to infer which positions had `r[i] = 0`, leaking bits of the receiver's secret scalar.

At minimum, the receiver silently accepts wrong OT outputs and produces an incorrect signature or multiplication share, breaking protocol correctness with no error returned.

---

### Likelihood Explanation

The attack requires only that the malicious sender craft a `msg3` with an empty `w0` vector. This is a straightforward wire-level manipulation: serialize count=0 for `w0`, count=`m` for `w1`. No cryptographic break is needed. The receiver performs no state check and no size lower-bound check on `w0`. The path is reachable from any protocol peer acting as the OT sender.

---

### Recommendation

Record the intended protocol variant as an explicit enum field in `ot_ext_protocol_ctx_t` (set during `step1_R2S` / `step2_S2R` / `step2_S2R_sender_one_input_random`). In `output_R`, assert or check this stored variant instead of inferring it from `w0.empty()`. Additionally, add an explicit guard:

```cpp
// In OT-Extension-2P mode, w0 must have exactly m entries.
if (!sender_one_input_random_mode && w0.size() != (size_t)m)
    return coinbase::error(E_FORMAT);
```

But the root fix is to not use `w0.empty()` as a mode discriminator at all — the mode must be fixed at setup time and stored, not inferred from attacker-supplied data.

---

### Proof of Concept

```cpp
// Deterministic unit test sketch (Full-OT-2P with injected empty w0)
ot_protocol_pvw_ctx_t sender_ctx, receiver_ctx;
bits_t r = crypto::gen_random_bits(m);
std::vector<buf_t> x0(m), x1(m);
// ... fill x0, x1 ...

// Honest sender step 1
sender_ctx.step1_S2R();
// Honest receiver step 2
receiver_ctx.step2_R2S(r, l);
// Honest sender step 3 (populates sender_ctx.ext.w0, w1)
sender_ctx.step3_S2R(x0, x1);

// ATTACK: copy w1 honestly but inject empty w0
receiver_ctx.ext.w0.clear();                    // empty w0
receiver_ctx.ext.w1 = sender_ctx.ext.w1;       // valid w1

// Receiver calls output_R — enters sender_one_input_random_mode
std::vector<buf_t> x_out;
error_t rv = receiver_ctx.output_R(m, x_out);
assert(rv == SUCCESS);  // succeeds with wrong values

// Verify output is wrong for r[i]=0 positions
for (int i = 0; i < m; i++) {
    buf_t expected = r[i] ? x1[i] : x0[i];
    if (!r[i]) assert(x_out[i] != expected);  // wrong output accepted silently
}
```

### Citations

**File:** src/cbmpc/protocol/ot.cpp (L281-286)
```cpp
  } else {
    if (x0.empty()) return coinbase::error(E_BADARG);
    l = bytes_to_bits(int(x0[0].size()));
    m = int(x0.size());
    w0.resize(m);
  }
```

**File:** src/cbmpc/protocol/ot.cpp (L358-364)
```cpp
error_t ot_ext_protocol_ctx_t::output_R(int m, std::vector<buf_t>& x) {
  bool sender_one_input_random_mode = w0.empty();
  if (!sender_one_input_random_mode) {
    if (m != int(w0.size())) return coinbase::error(E_FORMAT);
  }

  if (m != int(w1.size())) return coinbase::error(E_FORMAT);
```

**File:** src/cbmpc/protocol/ot.cpp (L370-386)
```cpp
  for (int i = 0; i < m; i++) {
    x[i] = hash_matrix_line(i, T[i], l);

    if (sender_one_input_random_mode) {
      if (bytes_to_bits(w1[i].size()) != l)
        return coinbase::error(E_BADARG, "sender_one_input_random_mode: w1[i] size mismatch");

      const buf_t w_sel = coinbase::ct_select_buf(r[i], w1[i], w_zero);
      x[i] ^= w_sel;
    } else {
      if (bytes_to_bits(w0[i].size()) != l || bytes_to_bits(w1[i].size()) != l)
        return coinbase::error(E_BADARG, "non-sender_one_input_random_mode: w0[i]/w1[i] size mismatch");

      const buf_t w_sel = coinbase::ct_select_buf(r[i], w1[i], w0[i]);
      x[i] ^= w_sel;
    }
  }
```

**File:** include-internal/cbmpc/internal/protocol/ot.h (L124-125)
```text
  auto msg2() { return std::tie(w0, w1); }
  auto msg2_delta() { return std::tie(w1); }
```

**File:** include-internal/cbmpc/internal/protocol/ot.h (L203-204)
```text
  auto msg3() { return ext.msg2(); }
  auto msg3_delta() { return ext.msg2_delta(); }
```

**File:** src/cbmpc/protocol/ecdsa_mp.cpp (L218-225)
```cpp
  for (int j = 0; j < n; j++) {
    if (ot_role_map[i][j] != ot_receiver) continue;

    std::vector<buf_t> X_bin;
    if (rv = ot[j].output_R(4 * theta, X_bin)) return rv;

    for (int l = 0; l < theta; l++)
      for (int t = 0; t < 4; t++) X[l][j][t] = bn_t::from_bin(X_bin[l * 4 + t]);
```
