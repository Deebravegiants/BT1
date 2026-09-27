# [H] vLLM: Security Check Bypass via assert Statement in Activation Function Loading Allows Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-q8gq-377p-jq3r
CVE: CVE-2026-41523
CWE: CWE-617, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-q8gq-377p-jq3r
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.22.0

## Details
### Summary

An `assert`-based security check in vLLM's activation function loading allows any unauthenticated attacker to achieve arbitrary code execution on the server by publishing a malicious HuggingFace model, when vLLM runs in Python optimized mode (`python -O` or `PYTHONOPTIMIZE=1`).

### Details

vLLM uses an `assert` statement at [`vllm/model_executor/layers/pooler/activations.py:48`](https://github.com/vllm-project/vllm/blob/main/vllm/model_executor/layers/pooler/activations.py#L48) as its sole security control to restrict which activation functions can be loaded from a HuggingFace model's `config.json`:

```python
# vllm/model_executor/layers/pooler/activations.py:35-53
function_name: str | None = None
if (
    hasattr(config, "sentence_transformers")
    and "activation_fn" in config.sentence_transformers
):
    function_name = config.sentence_transformers["activation_fn"]
elif (
    hasattr(config, "sbert_ce_default_activation_function")
    and config.sbert_ce_default_activation_function is not None
):
    function_name = config.sbert_ce_default_activation_function

if function_name is not None:
    assert function_name.startswith("torch.nn.modules."), (
        "Loading of activation functions is restricted to "
        "torch.nn.modules for security reasons"
    )
    fn = resolve_obj_by_qualname(function_name)()
```

Python's `assert` statements are stripped at compile time when running in optimized mode (`python -O` or `PYTHONOPTIMIZE=1`). When the assert is absent, the attacker-controlled `function_name` from the model's `config.json` is passed directly to [`resolve_obj_by_qualname()`](https://github.com/vllm-project/vllm/blob/main/vllm/utils/import_utils.py#L106) — an unrestricted import gadget:

```python
def resolve_obj_by_qualname(qualname: str) -> Any:
    module_name, obj_name = qualname.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, obj_name)
```

This is the same vulnerability class as **CVE-2017-1000433** (pysaml2 assert-based auth bypass), flagged by Bandit B101 and Ruff S101, and the reason Django proactively replaced all assert-based security checks (ticket #32508).

**Attacker-controlled input sources:**
- `config.sentence_transformers["activation_fn"]` (line 40)
- `config.sbert_ce_default_activation_function` (line 45)

**Affected call sites** — `get_act_fn()` is called via `resolve_classifier_act_fn()` from:
- `vllm/model_executor/layers/pooler/seqwise/poolers.py:122` — SequencePooler
- `vllm/model_executor/layers/pooler/tokwise/poolers.py:130` — TokenPooler

**Broader systemic risk:** `resolve_obj_by_qualname` is called from ~20 locations across the codebase with no validation of its own. Any future caller feeding user-controlled input to it without validation creates the same vulnerability class.

**Suggested fix:** Replace the `assert` with an explicit conditional raise:

```python
if not function_name.startswith("torch.nn.modules."):
    raise ValueError(
        "Loading of activation functions is restricted to "
        "torch.nn.modules for security reasons"
    )
```

### Impact

**Arbitrary code execution.** A malicious model author publishes a HuggingFace model with a crafted `config.json`. When a victim loads this model with vLLM running under `python -O` or `PYTHONOPTIMIZE=1`, arbitrary code executes during model initialization with the privileges of the vLLM process.

The attack requires:
1. Victim loads a malicious model from HuggingFace (user interaction)
2. vLLM runs under `python -O` or `PYTHONOPTIMIZE=1` (documented in production use)
3. Model uses a cross-encoder architecture (e.g. BERT or RoBERTa with sequence classification)

**Coordinated disclosure note:** This vulnerability was also reported via huntr.com on April 2, 2026 (https://huntr.com/bounties/dcb05b04-e625-41e7-adbc-bbae0cc2d64c). A GitHub Security Advisory was also filed because it is vLLM's stated preferred disclosure channel per SECURITY.md.

### Fix

A fix for this was introduced in this commit: https://github.com/vllm-project/vllm/commit/b3c7ffcab82c2439726f8cb213800f6f38c023d3

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-q8gq-377p-jq3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41523
- https://github.com/vllm-project/vllm/commit/b3c7ffcab82c2439726f8cb213800f6f38c023d3
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41523.json
- https://huntr.com/bounties/dcb05b04-e625-41e7-adbc-bbae0cc2d64c
- https://github.com/vllm-project/vllm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2300.yaml
- https://bugzilla.redhat.com/show_bug.cgi?id=2491582
- https://access.redhat.com/security/cve/CVE-2026-41523
- https://access.redhat.com/errata/RHSA-2026:62336
- https://access.redhat.com/errata/RHSA-2026:61629
- https://access.redhat.com/errata/RHSA-2026:61627
- https://access.redhat.com/errata/RHSA-2026:59151
- https://access.redhat.com/errata/RHSA-2026:59144
- https://access.redhat.com/errata/RHSA-2026:59139
- https://access.redhat.com/errata/RHSA-2026:59138
- https://access.redhat.com/errata/RHSA-2026:57390
- https://access.redhat.com/errata/RHSA-2026:57389
- https://access.redhat.com/errata/RHSA-2026:57387
- https://access.redhat.com/errata/RHSA-2026:57380
