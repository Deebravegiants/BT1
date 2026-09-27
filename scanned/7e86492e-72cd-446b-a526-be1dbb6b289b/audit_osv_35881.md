# [H] CVE-2026-15977

## Summary
Severity: High
Advisory: CVE-2026-15977
Aliases: GHSA-jx7q-p32r-7wx8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-15977
Type: osv

## Details
SGLang contains a credential leakage vulnerability in the /server_info endpoint, which will return API keys and SSL keyfile information when only the --admin-api-key is configured.

## References
- https://thoughts.apoorvdayal.com/posts/sglang-disclosures/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15977.json
- https://github.com/sgl-project/sglang/security/advisories/GHSA-jx7q-p32r-7wx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-15977
