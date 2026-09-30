# [C] Axolotl through 0.18.0 Remote Code Execution via Multipack Patching

## Summary
Severity: Critical
Advisory: CVE-2026-86169
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86169
Type: osv

## Details
Axolotl through 0.18.0 contains a remote code execution vulnerability in the multipack patch path where trust_remote_code defaults to None instead of False, causing the security guard to be bypassed. Attackers can execute arbitrary Python code by crafting a malicious Hugging Face model repository selected as base_model, which is loaded with hardcoded trust_remote_code=True during AutoModelForCausalLM.from_pretrained.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86169.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86169
- https://www.vulncheck.com/advisories/axolotl-through-0.18.0-remote-code-execution-via-multipack-patching
- https://github.com/axolotl-ai-cloud/axolotl/commit/b62d60b101eea7f32532ee3c0b17c2f2430a9262
- https://github.com/axolotl-ai-cloud/axolotl/pull/3858
- https://github.com/axolotl-ai-cloud/axolotl
- https://github.com/axolotl-ai-cloud/axolotl/blob/v0.18.0/src/axolotl/loaders/patch_manager.py#L794-L806
- https://github.com/axolotl-ai-cloud/axolotl/blob/v0.18.0/src/axolotl/monkeypatch/multipack.py#L86-L96
