# [M] CVE-2026-15974

## Summary
Severity: Medium
Advisory: CVE-2026-15974
Aliases: GHSA-x7w5-h7rp-gfp9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-15974
Type: osv

## Details
SGLang contains an SSRF and local file read in the multimodal generation endpoint /v1/chat/completions due to unsanitized image_url, allowing access to internal metadata, secrets, and services.

## References
- https://thoughts.apoorvdayal.com/posts/sglang-disclosures/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15974.json
- https://github.com/sgl-project/sglang/security/advisories/GHSA-x7w5-h7rp-gfp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-15974
