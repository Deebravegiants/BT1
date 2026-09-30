# [M] SillyTavern has Server-Side Request Forgery (SSRF) via Asset Download Endpoint that Allows Reading Internal Services

## Summary
Severity: Medium
Advisory: CVE-2026-26286
Aliases: GHSA-cccp-94vg-j92r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-26286
Type: osv

## Details
SillyTavern is a locally installed user interface that allows users to interact with text generation large language models, image generation engines, and text-to-speech voice models. In versions prior to 1.16.0, a Server-Side Request Forgery (SSRF) vulnerability in the asset download endpoint allows authenticated users to make arbitrary HTTP requests from the server and read the full response body, enabling access to internal services, cloud metadata, and private network resources. The vulnerability has been patched in the version 1.16.0 by introducing a whitelist domain check for asset download requests. It can be reviewed and customized by editing the `whitelistImportDomains` array in the `config.yaml` file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26286.json
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-cccp-94vg-j92r
- https://nvd.nist.gov/vuln/detail/CVE-2026-26286
