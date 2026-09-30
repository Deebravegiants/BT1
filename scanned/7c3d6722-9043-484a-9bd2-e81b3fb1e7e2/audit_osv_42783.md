# [H] peft Unsafe Deserialization via torch.load() Without weights_only in LoRA-GA and CorDA Modules

## Summary
Severity: High
Advisory: CVE-2026-71281
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71281
Type: osv

## Details
Hugging Face peft's LoRA-GA and CorDA initialization modules (src/peft/tuners/lora/corda.py lines ~102 and ~163, and src/peft/tuners/lora/loraga.py line ~101) call torch.load on config-specified cache/covariance files without weights_only=True, bypassing peft's own safe-loading wrapper used elsewhere in the codebase.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71281.json
- https://github.com/huggingface/peft
- https://github.com/huggingface/peft/blob/main/src/peft/tuners/lora/corda.py
- https://nvd.nist.gov/vuln/detail/CVE-2026-71281
