# [M] Typesense: Unauthenticated Denial of Service in the Typesense /multi_search Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-47216
Aliases: GHSA-fpx5-8c99-247j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47216
Type: osv

## Details
Typesense is a fast, typo-tolerant search engine. Prior to versions 29.1 and 30.2, there is an unauthenticated denial-of-service vulnerability in the /multi_search endpoint. A specially crafted request can trigger an unhandled exception during request processing, causing the server process to terminate. This issue can be exploited over the network without authentication and results in service unavailability. The duration of impact may vary depending on system configuration and dataset size. This issue has been patched in versions 29.1 and 30.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47216.json
- https://github.com/typesense/typesense/security/advisories/GHSA-fpx5-8c99-247j
- https://nvd.nist.gov/vuln/detail/CVE-2026-47216
