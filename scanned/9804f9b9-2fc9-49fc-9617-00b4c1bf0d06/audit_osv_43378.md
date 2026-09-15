# [M] vLLM: SSRF + arbitrary local file read in MiMoV2OmniMultiModalProcessor `_fetch_image` and audio loader bypass MediaConnector protections

## Summary
Severity: Medium
Advisory: CVE-2026-73560
Aliases: GHSA-4hhp-h66f-j5j7, PYSEC-2026-3934
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-73560
Type: osv

## Details
vLLM is an inference and serving engine for large language models. Prior to 0.26.0, the MiMoV2OmniMultiModalProcessor in vllm/transformers_utils/processors/mimo_v2_omni.py passes attacker-controlled image and audio strings through _fetch_image, requests.get, and Image.open instead of MediaConnector, bypassing allowed_media_domains and allowed_local_media_path protections and allowing server-side requests and reads of arbitrary files accessible to the vLLM process. This issue is fixed in version 0.26.0.

## References
- https://github.com/vllm-project/vllm/releases/tag/v0.26.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73560.json
- https://github.com/vllm-project/vllm/security/advisories/GHSA-4hhp-h66f-j5j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-73560
- https://github.com/vllm-project/vllm/commit/54503ecec0f3ac31e5ecfc5f28652e4cc42307b5
- https://github.com/vllm-project/vllm/pull/43117
