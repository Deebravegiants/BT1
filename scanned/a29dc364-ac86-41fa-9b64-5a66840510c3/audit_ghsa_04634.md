# [M] vLLM's Artifact Pin Decay allows pinned deployments to load unpinned code, weights, and processors

## Summary
Severity: Medium
Advisory: GHSA-3ww4-5jv9-j5gm
CVE: CVE-2026-47155
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-3ww4-5jv9-j5gm
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.22.0

## Details
### Summary

vLLM's revision pinning controls do not consistently apply to all artifacts loaded for a model. A deployment that supplies `--revision` or `--code-revision` can still load dynamic code, GGUF files, image processors, retrieval side weights, or same-repository subfolder weights/config from an unpinned/default revision.

This is a supply-chain integrity issue for pinned vLLM deployments. Operators can believe they are serving a reviewed model revision while vLLM resolves behavior-affecting nested or sibling artifacts outside that reviewed revision.

### Details

The expected invariant is:

> When a vLLM operator supplies a model or code revision pin, every code, config, processor, weight file, side weight, and same-repository subfolder artifact loaded as part of that model should resolve under that pin unless vLLM exposes and enforces a separate explicit pin for that artifact.

Current `main` was verified affected at commit `3795d7acf431980e62e738493f437ae2a51549da`.

Affected source boundaries:

- `vllm/model_executor/models/registry.py:1045-1051` and `:1058-1064`
  - `_try_resolve_transformers()` passes `revision=model_config.revision` and `trust_remote_code=model_config.trust_remote_code`, but omits `code_revision=model_config.code_revision` for external `auto_map` dynamic module imports.
- `vllm/model_executor/model_loader/gguf_loader.py:58-60`
  - The direct-file GGUF form `repo/file.gguf` calls `hf_hub_download(repo_id=repo_id, filename=filename)` without passing `revision`.
- `vllm/model_executor/models/roberta.py:203-209`
  - BGE-M3 secondary sparse and ColBERT side weights are declared with `revision=None`.
- `vllm/model_executor/models/kimi_k25.py:111-114`
  - Kimi-K2.5 calls `cached_get_image_processor()` without passing `model_config.revision`.
- `vllm/model_executor/models/kimi_audio.py:92-95`
  - Kimi-Audio loads Whisper config from the `whisper-large-v3` subfolder without a `revision` argument.
- `vllm/model_executor/models/kimi_audio.py:425-430`
  - Kimi-Audio declares same-repository `whisper-large-v3` secondary weights with `revision=None`.
- `vllm/model_executor/model_loader/default_loader.py:287-301`
  - The default loader preserves `model_config.revision` for the primary source, then consumes model-supplied secondary sources as declared.

The strongest example is Kimi-Audio: the primary `moonshotai/Kimi-Audio-7B-Instruct` weights preserve the configured model revision, but the same-repository `whisper-large-v3` audio tower config/weights do not. A pinned Kimi-Audio deployment can therefore load the Whisper subfolder outside the audited revision.

This report does not claim a `trust_remote_code=False` bypass, unauthenticated RCE, or real artifact compromise. The issue is improper propagation of explicit artifact pins across supported loader paths.

### Impact

Affected users are operators who pin vLLM model deployments to a reviewed Hugging Face revision for safety review, provenance, rollback, or reproducibility. The impact is that the pin does not reliably describe the full set of artifacts vLLM serves. Even when the operator selects an audited revision, vLLM can resolve behavior-affecting secondary artifacts from the repository default branch or another mutable ref.

Depending on the model path, the unpinned artifact can be dynamic model code, a GGUF file, an image processor, retrieval side weights, or the same-repository Kimi-Audio Whisper subfolder weights/config.

This breaks the operational guarantee of a pinned deployment: "serve the exact artifact set I reviewed." A later change to an unpinned secondary artifact can alter model behavior without changing the operator's configured revision, making review, rollback, incident response, and audit records unreliable.

### Occurrences

- `vllm/model_executor/models/kimi_k25.py` L111-L114 — Kimi-K2.5 loads its image processor with `cached_get_image_processor()` but does not pass `self.ctx.model_config.revision`. The processor can therefore resolve from the default repository revision even when the model deployment is pinned.
- `vllm/model_executor/models/kimi_audio.py` L425-L430 — Kimi-Audio declares same-repository `whisper-large-v3` secondary weights with `revision=None`. A pinned Kimi-Audio deployment can therefore load the Whisper audio tower weights from an unpinned/default revision.
- `vllm/model_executor/models/kimi_audio.py` L92-L95 — Kimi-Audio loads Whisper config from the same repository's `whisper-large-v3` subfolder without passing the top-level model revision. The config for this behavior-affecting subcomponent can be resolved outside the audited model revision.
- `vllm/model_executor/models/registry.py` L1058-L1064 — The later dynamic model-class resolution repeats the same pin-decay pattern: it forwards `revision` and `trust_remote_code`, but omits `code_revision`. This means an operator-provided code pin is not enforced at the dynamic module loader boundary.
- `vllm/model_executor/model_loader/gguf_loader.py` L58-L60 — The direct GGUF form `repo/file.gguf` calls `hf_hub_download(repo_id=repo_id, filename=filename)` without passing `model_config.revision`. A deployment that pins the model revision can therefore resolve this GGUF file from the repository default revision.
- `vllm/model_executor/models/registry.py` L1045-L1051 — `try_get_class_from_dynamic_module()` is called for external `auto_map` config/model classes with `revision=model_config.revision`, but without forwarding `model_config.code_revision`. When `--code-revision` is set, this dynamic module resolution can still fall back to the default code revision instead of the audited code revision.
- `vllm/model_executor/models/roberta.py` L203-L209 — `BgeM3EmbeddingModel` creates same-repository secondary sparse/ColBERT weight sources with `revision=None`. The primary model revision is not propagated to these side weights, so they can be downloaded outside the operator-selected model revision.

### Fixes

This was fixed in: https://github.com/vllm-project/vllm/pull/42616

___

Originally filed via huntr: https://huntr.com/bounties/3f1e24c0-87d2-4f6c-a705-820f380879ac.

The vLLM maintainer (Russell Bryant) redirected the report to the private GHSA channel. Offline proof bundle (`vllm_artifact_pin_decay_bundle_verify.py` + `bundle-verification-20260430T143506Z.json`) is available upon request.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-3ww4-5jv9-j5gm
- https://nvd.nist.gov/vuln/detail/CVE-2026-47155
- https://github.com/vllm-project/vllm/pull/42616
- https://github.com/vllm-project/vllm/commit/d26a28ab033697f55a1414b5b0435de7cd6045b6
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2301.yaml
- https://github.com/vllm-project/vllm
- https://huntr.com/bounties/3f1e24c0-87d2-4f6c-a705-820f380879ac
