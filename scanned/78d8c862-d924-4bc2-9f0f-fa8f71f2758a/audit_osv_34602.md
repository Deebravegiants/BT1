# [M] c-ares has a Use After Free vulnerability when connection is cleaned up after error

## Summary
Severity: Medium
Advisory: CVE-2025-62408
Aliases: GHSA-jq53-42q6-pqr5
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-62408
Type: osv

## Details
c-ares is an asynchronous resolver library. Versions 1.32.3 through 1.34.5  terminate a query after maximum attempts when using read_answer() and process_answer(), which can cause a Denial of Service. This issue is fixed in version 1.34.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62408.json
- https://github.com/c-ares/c-ares/security/advisories/GHSA-jq53-42q6-pqr5
- https://nvd.nist.gov/vuln/detail/CVE-2025-62408
- https://github.com/c-ares/c-ares/commit/714bf5675c541bd1e668a8db8e67ce012651e618
