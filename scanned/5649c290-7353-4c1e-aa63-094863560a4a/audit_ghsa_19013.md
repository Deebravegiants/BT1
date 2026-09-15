# [H] vLLM vulnerable to DoS with incorrect shape of multimodal embedding inputs

## Summary
Severity: High
Advisory: GHSA-pmqf-x6x8-p7qw
CVE: CVE-2025-62372
CWE: CWE-129
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-pmqf-x6x8-p7qw
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.5.5 <0.11.1

## Details
### Summary

Users can crash the vLLM engine serving multimodal models by passing multimodal embedding inputs with correct `ndim` but incorrect `shape` (e.g. hidden dimension is wrong), regardless of whether the model is intended to support such inputs (as defined in the Supported Models page).

The issue has existed ever since we added support for image embedding inputs, i.e. #6613 (released in v0.5.5)

### Details

Using image embeddings as an example:

- For models that support image embedding inputs, the engine crashes when scattering the embeddings to `inputs_embeds` (mismatched shape)
- For models that don't support image embedding inputs, the engine crashes when validating the inputs inside `get_input_embeddings` (validation fails).

This happens because we only validate `ndim` of the tensor, but not the full shape, in input processor (via `MultiModalDataParser`).

### Impact

- Denial of service by crashing the engine

### Mitigation

- Use API key to limit access to trusted users.
- Set `--limit-mm-per-prompt` to 0 for all non-text modalities to ban multimodal inputs, which includes multimodal embedding inputs. However, the model would then only accept text, defeating the purpose of using a multi-modal model.

### Resolution

- https://github.com/vllm-project/vllm/pull/27204

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-pmqf-x6x8-p7qw
- https://nvd.nist.gov/vuln/detail/CVE-2025-62372
- https://github.com/vllm-project/vllm/pull/27204
- https://github.com/vllm-project/vllm/pull/6613
- https://github.com/vllm-project/vllm/commit/58fab50d82838d5014f4a14d991fdb9352c9c84b
- https://github.com/advisories/GHSA-pmqf-x6x8-p7qw
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2019.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
