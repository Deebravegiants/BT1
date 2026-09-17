# [M] FreshRSS vulnerable to DoS by malicious feed entry loading logout URL

## Summary
Severity: Medium
Advisory: CVE-2025-31482
Aliases: GHSA-vpmc-3fv2-jmgp
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-06-04
Source: https://osv.dev/vulnerability/CVE-2025-31482
Type: osv

## Details
FreshRSS is a self-hosted RSS feed aggregator. A vulnerability in versions prior to 1.26.2 causes a user to be repeatedly logged out after fetching a malicious feed entry, effectively causing that user to suffer denial of service. Version 1.26.2 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31482.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-vpmc-3fv2-jmgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-31482
