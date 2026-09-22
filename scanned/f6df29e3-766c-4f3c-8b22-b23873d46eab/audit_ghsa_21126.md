# [H] Protected fields exposed via LiveQuery

## Summary
Severity: High
Advisory: GHSA-crrq-vr9j-fxxh
CVE: CVE-2022-31112
CWE: CWE-200, CWE-212
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-07-06
Source: https://github.com/advisories/GHSA-crrq-vr9j-fxxh
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.13
- npm: `parse-server` — affected >=5.0.0 <5.2.4

## Details
### Impact

Parse Server LiveQuery does not remove protected fields in classes, passing them to the client.

### Patches
The LiveQueryController now removes protected fields from the client response.

### Workarounds
Use `Parse.Cloud.afterLiveQueryEvent` to manually remove protected fields.

### References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-crrq-vr9j-fxxh
- https://github.com/parse-community/parse-server

### For more information
If you have any questions or comments about this advisory:
- For questions or comments about this vulnerability visit our [community forum](http://community.parseplatform.org/) or [community chat](http://chat.parseplatform.org/)
- Report other vulnerabilities at [report.parseplatform.org](https://report.parseplatform.org/)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-crrq-vr9j-fxxh
- https://nvd.nist.gov/vuln/detail/CVE-2022-31112
- https://github.com/parse-community/parse-server/issues/8073
- https://github.com/parse-community/parse-server/pull/8074
- https://github.com/parse-community/parse-server/commit/054f3e6ab01d66a0dcfb77725af28eac1485b375
- https://github.com/parse-community/parse-server/commit/309f64ced8700321df056fb3cc97f15007a00df1
- https://github.com/parse-community/parse-server/commit/9fd4516cde5c742f9f29dd05468b4a43a85639a6
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/5.2.4
