# [M] WeGIA  allows Uncontrolled Resource Consumption via the errorstr parameter

## Summary
Severity: Medium
Advisory: CVE-2025-53530
Aliases: GHSA-562r-xgj9-2r7p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-53530
Type: osv

## Details
WeGIA is a web manager for charitable institutions. The Wegia server has a vulnerability that allows excessively long HTTP GET requests to a specific URL. This issue arises from the lack of validation for the length of the errorstr parameter. Tests confirmed that the server processes URLs up to 8,142 characters, resulting in high resource consumption, elevated latency, timeouts, and read errors. This makes the server susceptible to Denial of Service (DoS) attacks.  This vulnerability is fixed in 3.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53530.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-562r-xgj9-2r7p
- https://nvd.nist.gov/vuln/detail/CVE-2025-53530
