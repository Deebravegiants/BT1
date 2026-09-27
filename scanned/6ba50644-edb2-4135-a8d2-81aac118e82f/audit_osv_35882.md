# [H] CVE-2026-15978

## Summary
Severity: High
Advisory: CVE-2026-15978
Aliases: GHSA-cpqq-22v3-2wfm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-15978
Type: osv

## Details
SGLang contains a model weight exfiltration vulnerability when no API keys are configured, as SGLang will expose two endpoints that allow a remote attacker to trigger distributed weight broadcasting using NCCL and then triggering data transfer, attackers can exfiltrate all model weights.

## References
- https://thoughts.apoorvdayal.com/posts/sglang-disclosures/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15978.json
- https://github.com/sgl-project/sglang/security/advisories/GHSA-cpqq-22v3-2wfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-15978
