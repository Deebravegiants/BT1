# [H] Diffusers: TOCTOU Trust Remote Code Bypass

## Summary
Severity: High
Advisory: GHSA-7wx4-6vff-v64p
CVE: CVE-2026-45804
CWE: CWE-367
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-7wx4-6vff-v64p
Type: github-advisory

## Affected
- PyPI: `diffusers` — affected >=0 <0.38.0

## Details
## Background

This vulnerability is found in the `diffusers` package - the `transformers`-equivalent library for diffusion models.

It is found in the `DiffusionPipeline.from_pretrained` flow, which is used to load a pipeline from the HuggingFace Hub.

This function has a `trust_remote_code` guard: if the repository’s `model_index.json` references a custom pipeline class defined in a `.py` file in the repo, the load is blocked unless `trust_remote_code=True` is explicitly passed:

```
ValueError: The repository for attacker/repo contains custom code in pipeline.py
which must be executed to correctly load the model. You can inspect the repository
content at https://hf.co/attacker/repo/blob/main/pipeline.py.
Please pass the argument `trust_remote_code=True` to allow custom code to be run.
```

The vulnerability allows arbitrary code execution through the custom pipeline flow from a Hub repo, with no `custom_pipeline` or `trust_remote_code` kwargs passed. The `from_pretrained` call succeeds and returns a functional pipeline.

---

## Naive Flow

`DiffusionPipeline.from_pretrained` begins by popping all relevant arguments from `kwargs` into local variables, then calls `DiffusionPipeline.download()` to fetch the repo files:

```python
# pipeline_utils.py:853
cached_folder = cls.download(
    pretrained_model_name_or_path,
    ...
    custom_pipeline=custom_pipeline,
    trust_remote_code=trust_remote_code,
    ...
)
```

Inside `download()`, `model_index.json` is fetched first as a standalone file via `hf_hub_download`:

```python
# pipeline_utils.py:1636
config_file = hf_hub_download(
    pretrained_model_name,
    cls.config_name,
    ...
)
config_dict = cls._dict_from_json_file(config_file)
```

This config is used to detect custom pipeline code and enforce the trust check:

```python
# pipeline_utils.py:1672
if custom_pipeline is None and isinstance(config_dict["_class_name"], (list, tuple)):
    custom_pipeline = config_dict["_class_name"][0]

load_pipe_from_hub = custom_pipeline is not None and f"{custom_pipeline}.py" in filenames

if load_pipe_from_hub and not trust_remote_code:
    raise ValueError(...)
```

After the check passes, `snapshot_download` then fetches all files and saves them to disk:

```python
# pipeline_utils.py:1778
cached_folder = snapshot_download(
    pretrained_model_name,
    ...
    revision=revision,
    allow_patterns=allow_patterns,
    ...
)
```

Back in `from_pretrained`, the config is read a second time from the downloaded snapshot, and`_resolve_custom_pipeline_and_cls` reads the config to re-check if custom code needs to be loaded:

```python
# pipeline_loading_utils.py:974
def _resolve_custom_pipeline_and_cls(folder, config, custom_pipeline):
    custom_class_name = None
    if os.path.isfile(os.path.join(folder, f"{custom_pipeline}.py")):
        custom_pipeline = os.path.join(folder, f"{custom_pipeline}.py")
    elif isinstance(config["_class_name"], (list, tuple)) and os.path.isfile(
        os.path.join(folder, f"{config['_class_name'][0]}.py")
    ):
        custom_pipeline = os.path.join(folder, f"{config['_class_name'][0]}.py")
        custom_class_name = config["_class_name"][1]

    return custom_pipeline, custom_class_name
```

If the config points to a `.py` file, it is imported.

---

## The Vulnerability

`hf_hub_download` and `snapshot_download` are two independent HTTP calls to the Hub, both resolving the repository’s default branch (if `revision=None`) to its current HEAD at call time. There is no atomicity guarantee between them - if the repository is updated between the two calls, they will resolve to different commits and download different content, with no warning displayed to the user.

The trust check in `download()` operates on the content fetched by `hf_hub_download` (commit A). The `snapshot_download` call that immediately follows can silently fetch a newer commit (commit B). The config in the newer commit will be the one parsed by `_resolve_custom_pipeline_and_cls`.

**Therefore, it’s possible to introduce remote code into the repo between the two calls, bypassing the trust check.**

The race window is everything between the two Hub calls inside `download()`:

```python
# pipeline_utils.py:1636
config_file = hf_hub_download(...)   # ← sees commit A, trust check passes

# ... filenames processing, pattern building, pipeline_is_cached check ...
# ~~~ ATTACKER PUSHES COMMIT B HERE ~~~

# pipeline_utils.py:1778
cached_folder = snapshot_download(...)  # ← sees commit B, downloads pipeline.py
```

For the exploit, commit A carries a clean config with `_class_name` as a plain string, which causes `load_pipe_from_hub` to be `False` and the trust check to pass. Commit B changes `_class_name` to a list and adds `pipeline.py`:

**Commit A - `model_index.json`:**

```json
{
  "_class_name": "FluxPipeline",
  "_diffusers_version": "0.31.0"
}
```

**Commit B - `model_index.json`:**

```json
{
  "_class_name": ["pipeline", "FluxPipeline"],
  "_diffusers_version": "0.31.0"
}
```

When `from_pretrained` reads the snapshot after `download()` returns, `config["_class_name"]` is now a list, `pipeline.py` exists on disk (fetched by `snapshot_download`), and `_resolve_custom_pipeline_and_cls` resolves `custom_pipeline` to the local path of that file. `_get_pipeline_class` then imports it - with no trust check at this point in the code.

---

## PoC

1. Create a Hub repo with commit A’s `model_index.json` (plain string `_class_name`).
2. Run `DiffusionPipeline.from_pretrained("attacker/repo")` with a breakpoint set at `pipeline_utils.py:1778` (the `snapshot_download` call). This is for the window to be large enough to manually respond to it.
3. When execution pauses at the breakpoint, push commit B: update `model_index.json` to use a list `_class_name` and add `pipeline.py`.
4. Resume execution.
5. `snapshot_download` fetches commit B; `/tmp/pwned` is written during the subsequent `_get_pipeline_class` call.

---

## Constraints

- Does not apply when `revision` is pinned to a specific commit hash - both Hub calls resolve to the same content.
- Does not apply when loading from a local directory.
- If all expected files are already present in the local HF cache, `download()` returns early before reaching `snapshot_download` (line 1767 early-return), closing the race window. The exploit therefore requires a first (or forced) download.

---

## Exploitability

The window between the two calls is very short. Local testing resulted in a window of approximately ~0.5 seconds for the attacker to push the change. This is, of course, unfeasible to accomplish for each and every new download. However, given a popular repo with many downloads per day, one may achieve **statistical success** by changing the repo’s state every once in a while or every few seconds, with some percentage of downloaders falling on the exact window. 

---

## Impact

The vulnerability is a silent RCE - it allows arbitrary code to be loaded through the custom pipeline flow from a Hub repo, with no `custom_pipeline` or `trust_remote_code` kwargs. The `from_pretrained` call succeeds and returns a fully functional pipeline.

## References
- https://github.com/huggingface/diffusers/security/advisories/GHSA-7wx4-6vff-v64p
- https://nvd.nist.gov/vuln/detail/CVE-2026-45804
- https://github.com/huggingface/diffusers/issues/13446
- https://github.com/huggingface/diffusers/pull/13448
- https://github.com/huggingface/diffusers/commit/a37f6f8394ac2a7ee8360c3abea811efe54512b1
- https://github.com/huggingface/diffusers
- https://github.com/huggingface/diffusers/releases/tag/v0.38.0
- https://github.com/pypa/advisory-database/tree/main/vulns/diffusers/PYSEC-2026-2446.yaml
