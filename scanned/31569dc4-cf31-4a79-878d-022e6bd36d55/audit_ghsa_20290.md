# [H] Invalid file request can crash server

## Summary
Severity: High
Advisory: GHSA-xw6g-jjvf-wwf9
CVE: CVE-2022-31089
CWE: CWE-252
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-20
Source: https://github.com/advisories/GHSA-xw6g-jjvf-wwf9
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.12
- npm: `parse-server` — affected >=5.0.0 <5.2.3

## Details
### Impact
Certain types of invalid files requests are not handled properly and can crash the server. If you are running multiple Parse Server instances in a cluster, the availability impact may be low; if you are running Parse Server as a single instance without redundancy, the availability impact may be high.

### Patches
To prevent this, invalid requests are now properly handled.

### Workarounds
None

### References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-xw6g-jjvf-wwf9
- https://github.com/parse-community/parse-server

### For more information
- For questions or comments about this vulnerability visit our [community forum](http://community.parseplatform.org/) or [community chat](http://chat.parseplatform.org/)
- Report other vulnerabilities at [report.parseplatform.org](https://report.parseplatform.org/)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-xw6g-jjvf-wwf9
- https://nvd.nist.gov/vuln/detail/CVE-2022-31089
- https://github.com/parse-community/parse-server/commit/5be375dec2fa35425c1003ae81c55995ac72af92
- https://github.com/parse-community/parse-server
