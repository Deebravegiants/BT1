# [H] lmdeploy vulnerable to Arbitrary Code Execution via Insecure Deserialization in torch.load()

## Summary
Severity: High
Advisory: CVE-2025-67729
Aliases: GHSA-9pf3-7rrr-x5jh, PYSEC-2026-1578
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-26
Source: https://osv.dev/vulnerability/CVE-2025-67729
Type: osv

## Details
LMDeploy is a toolkit for compressing, deploying, and serving LLMs. Prior to version 0.11.1, an insecure deserialization vulnerability exists in lmdeploy where torch.load() is called without the weights_only=True parameter when loading model checkpoint files. This allows an attacker to execute arbitrary code on the victim's machine when they load a malicious .bin or .pt model file. This issue has been patched in version 0.11.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67729.json
- https://github.com/InternLM/lmdeploy/security/advisories/GHSA-9pf3-7rrr-x5jh
- https://nvd.nist.gov/vuln/detail/CVE-2025-67729
- https://github.com/InternLM/lmdeploy/commit/eb04b4281c5784a5cff5ea639c8f96b33b3ae5ee
