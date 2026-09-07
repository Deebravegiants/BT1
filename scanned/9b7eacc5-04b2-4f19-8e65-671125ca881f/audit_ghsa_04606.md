# [M] tract-nnef: integer overflow in NNEF `.dat` tensor parser yields an out-of-bounds read on model load

## Summary
Severity: Medium
Advisory: GHSA-x5mv-8wgw-29hg
CVE: CVE-2026-55093
CWE: CWE-125, CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-x5mv-8wgw-29hg
Type: github-advisory

## Affected
- crates.io: `tract-nnef` — affected >=0.23.0 <0.23.1
- crates.io: `tract-nnef` — affected >=0.22.0 <0.22.2
- crates.io: `tract-nnef` — affected >=0 <0.21.16

## Details
- **Component:** `tract-nnef` (`nnef/src/tensors.rs::read_tensor`) + `tract-data` (`data/src/tensor.rs`)
- **Affected versions:** `< 0.21.16`, `0.22.0`–`0.22.2`, `0.23.0`–`0.23.1` — the dense `DatLoader` path was unguarded across all three release lines; patched in 0.21.16 / 0.22.2 / 0.23.1
- **Class:** CWE-190 (integer overflow) → CWE-125 (out-of-bounds read)
- **Trigger:** loading a crafted NNEF model archive (`*.nnef.tgz` / `*.nnef.tar` / dir) via the public `tract_nnef::nnef().model_for_path` / `model_for_read`
- **Impact:** `read_tensor` returns a memory-unsafe tensor (reported `len` 2^61 over a 56-byte heap allocation). Always-on primitive: a **bounded heap out-of-bounds read** during model build (`as_uniform`), an adjacent-heap information-disclosure reachable via the public load API. The resulting slice is an unsound `from_raw_parts(ptr, 2^61)` that **SIGSEGVs (DoS)** on any access past the mapped region (demonstrated by direct access). No out-of-bounds write and no RCE were achieved — tract's const-folding/`as_uniform` fast-paths fold simple consuming graphs without the full read.
- **Severity:** Medium

## Summary

`read_tensor` builds a tensor `shape` from attacker-controlled 32-bit dimensions and computes the element count `len = product(shape)` and the byte allocation `product(shape) * size_of(dt)` with **unchecked `usize` arithmetic**. In `--release` (no `overflow-checks`), both products wrap modulo 2^64. An attacker chooses dimensions so that the wrapped products collapse to a small value that satisfies the header consistency check, while the *true* element count remains astronomically large. `read_tensor` returns `Ok` with a `Tensor` whose reported `len` (e.g. 2^61+7) is far larger than its backing heap allocation (e.g. 56 bytes). The unchecked slice accessor `as_slice_unchecked` (`from_raw_parts(ptr, self.len)`) then produces a slice spanning ~18 exabytes over a 56-byte buffer. The out-of-bounds read fires automatically during model build (no inference required), reachable through the default `DatLoader` resource loader.

## Root cause

`nnef/src/tensors.rs`, `read_tensor`:

```
let shape: TVec<usize> = header.dims[0..header.rank as usize].iter().map(|d| *d as _).collect();
let len = shape.iter().product::<usize>();                       // (1) unchecked, wraps
...
} else if header.bits_per_item != u32::MAX
    && len * (header.bits_per_item as usize / 8) != header.data_size_bytes as usize  // (2) wrapped == u32
{
    bail!(...);
}
...
let mut tensor = unsafe { Tensor::uninitialized_dt(dt, &shape)? };   // (3) alloc off the same wrapped product
...
reader.read_exact(plain.as_bytes_mut())?;                            // storage-bounded read, no overflow here
Ok(tensor)
```

`data/src/tensor.rs`, `uninitialized_aligned_dt`:

```
let bytes = shape.iter().cloned().product::<usize>() * dt.size_of();  // (3) wraps to the same small value
let storage = ... Blob::new_for_size_and_align(bytes, alignment) ...;
...
tensor.update_strides_and_len();                                     // len = product(shape), wraps, no clamp
```

The three quantities — the consistency-check LHS `(2)`, the allocation `(3)`, and the reported `len` — are all the same wrapped `product(shape)*size_of`, so they stay mutually consistent and **the consistency check at `(2)` cannot catch the overflow**. `data_size_bytes` is a `u32`, so the attacker simply sets it to the wrapped value.

Corruption sink — `data/src/tensor.rs::as_slice_unchecked` (and `data/src/tensor/plain_view.rs::as_slice_unchecked`):

```
if self.storage.byte_len() == 0 { &[] }
else { std::slice::from_raw_parts(self.as_ptr_unchecked(), self.len()) }  // len = 2^61 over a 56-byte alloc
```

The only guard is `byte_len() == 0`. A small **non-zero** allocation defeats it and yields an unsound oversized slice.

## Witness (F64)

```
dims          = [33955849, 7005787, 359, 3, 3, 3]   (rank 6, each <= u32::MAX)
product(shape)= 2_305_843_009_213_693_959 = 2^61 + 7
bits_per_item = 64 (F64), item_type = 0, item_type_vendor = 0
data_size_bytes = 56            # == (2^61+7)*8 mod 2^64
```

- `len * (bits/8) mod 2^64 = (2^61+7)*8 mod 2^64 = 56 == data_size_bytes` → consistency check passes.
- allocation = `(2^61+7)*8 mod 2^64 = 56` bytes (7 × F64).
- reported `len` = `2^61+7` elements.

Only the `is_copy()` numeric arms (F16/F32/F64/int, and likely the `complex` arms) are exploitable. F64 is the cleanest (`bits/8` divides evenly). The `bool`, `String`, and block-quant paths are each guarded by an independent mechanism (size_of==1 prevents byte/element divergence; `String` bails on a missing `num_traits::Zero` impl; block-quant has its own `ensure!(expected_len == data_size_bytes)` and uses non-plain `Exotic` storage).

## Reachability (load-time, public API)

```
nnef().model_for_read(tar)
  -> proto_model_for_read                       nnef/src/framework.rs:303
    -> DatLoader.try_load (any *.dat)            nnef/src/resource.rs:97   (default loader, framework.rs:33)
      -> read_tensor -> Ok(Tensor{len=2^61+7, storage=56B})   nnef/src/tensors.rs:61
  -> into_typed_model -> variable() fragment     nnef/src/ops/nnef/deser.rs:74
       ensure!(tensor.shape() == &*shape)        deser.rs:122  (attacker matches shape in graph.nnef -> passes)
    -> Const::new -> wire_node                   core/src/model/typed.rs:67
      -> Const::output_facts                     core/src/ops/konst.rs:54
        -> TypedFact::try_from                   core/src/model/fact.rs:459
          -> Tensor::as_uniform -> is_uniform_t::<f64>   data/src/tensor.rs:1099
            -> as_slice_unchecked::<f64>         data/src/tensor.rs:1044
              -> from_raw_parts(ptr, 2^61+7) over 56-byte buffer -> OOB READ
```

No shape-vs-storage re-validation exists anywhere on this path (`proto.validate()` checks only the AST; `Const::new` checks only `is_plain`; `check_for_access` checks only the datum type; even the *safe* `PlainView::as_slice` does `from_raw_parts(ptr, self.len)` with no length guard).

## Execution (proof of concept)

Reproduced against the crate at the affected revision, `--release`, x86_64-linux. Three scenarios:

1. **Direct `read_tensor`** — feed the crafted 128-byte header + 56-byte payload:
   - `read_tensor -> Ok`, `shape=[33955849,7005787,359,3,3,3]`, `len()=2305843009213693959`, `as_bytes().len()=56`, `as_slice::<f64>().len()=2305843009213693959`.
   - `s[7]` (first element past the 56-byte allocation) returns `0x0000000000000041` → **heap OOB read** (adjacent-heap disclosure).
   - `s[1<<40]` → **SIGSEGV** (signal 11).
2. **Public load API** — build a malicious `.nnef.tar` (`graph.nnef` with `variable(label='weights', shape=[...])` + `weights.dat`) and call `nnef().model_for_read()`:
   - returns `Ok` with one `Const` node, `out[0].fact.uniform=Some(...)`, `len()=2305843009213693959` over a 56-byte buffer → confirms `as_uniform`/`is_uniform_t`/`as_slice_unchecked` performed an **OOB read on load** (bounded over-read here because `is_uniform`'s `.all()` short-circuits on the uniform `0x41` payload).
3. **Optimized graph** — same archive but the const is consumed (`output = mul(weights, weights)`), then `into_optimized` / `run`:
   - **Does not crash.** With both a uniform (`0x41×56`) and a non-uniform (`0..56`) payload, `into_optimized` const-folds `mul(const, const)` to a single node **without a full-length materialization** of the oversized const, and `run` completes. A reliable arbitrary-length crash through a *normal optimized graph* was therefore NOT demonstrated; the always-on primitive is the bounded load-time over-read (scenario 2), and the wild-slice SIGSEGV is shown via direct access (scenario 1).

Runnable PoC sources are available to the maintainers on request.

## Detection

- **Static:** flag `*.iter().product::<usize>()` over externally-controlled dimensions without `checked_*`/`try_into`, especially when the result feeds an allocation and a separately-tracked `len`.
- **Runtime / fleet:** crash telemetry showing SIGSEGV inside `is_uniform_t` / `from_raw_parts` during NNEF model load; an ASAN build flags `heap-buffer-overflow READ` in `read_tensor`→`as_uniform`.
- **Input filter (compensating):** reject NNEF `.dat` tensors where `product(dims)` overflows `u64`, or where `product(dims) * size_of(dt) != data_size_bytes` computed in **checked** arithmetic, before constructing the tensor.
- **YARA-ish heuristic for `.dat` blobs:** NNEF magic `4E EF 01 00`, `rank<=8`, and any `dim >= 0x10000` whose checked product with the others overflows.

## Mitigation (suggested fix)

In `read_tensor`, compute the element count and byte size with checked arithmetic and reject on overflow, mirroring the guard already present on the block-quant path (`ensure!(expected_len == data_size_bytes)` added in `eacd13ccb`):

```
let len = shape.iter().try_fold(1usize, |a, &d| a.checked_mul(d))
    .context("tensor shape product overflows usize")?;
let byte_size = len.checked_mul(dt.size_of())
    .context("tensor byte size overflows usize")?;
ensure!(byte_size == header.data_size_bytes as usize, "shape/len vs data_size_bytes mismatch");
```

Defense in depth: make `Tensor::uninitialized_aligned_dt` reject when `product(shape)*size_of` overflows, and add a `len * size_of == storage.byte_len()` invariant check in the `as_slice*` accessors (or at `Tensor` construction) so a `len`/storage mismatch can never reach `from_raw_parts`.

Mapping: CWE-190, CWE-125; mitigations align with input validation (OWASP ASVS V5) and safe integer handling (CERT INT32-C analogue).

## Prior art / why this is not already fixed

- `eacd13ccb` (2026-03-23, "Add blob-size validation to BlockQuantStorage constructors") added overflow/blob-size validation **only to the block-quant path**; the dense `DatLoader`/`read_tensor` path was left unguarded. The maintainers fixed the sibling and missed this one.
- PR #745 ("Fix UB by creating uninit Tensors with a non-null pointer") is a *different* UB (null base pointer on zero-length slices) in the same module family.
- No CVE / RustSec / GHSA / OSV / Huntr entry matches this bug; last change to `nnef/src/tensors.rs` predates HEAD and added no overflow guard to the dense path.

---

Reported by: s1ko (s1ko@riseup.net · github.com/s1ko)

## References
- https://github.com/sonos/tract/security/advisories/GHSA-x5mv-8wgw-29hg
- https://github.com/sonos/tract
