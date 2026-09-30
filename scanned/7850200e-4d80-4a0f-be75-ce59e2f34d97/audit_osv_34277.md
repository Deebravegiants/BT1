# [H] CVE-2025-57349

## Summary
Severity: High
Advisory: CVE-2025-57349
Aliases: GHSA-xfqm-j7pc-xrfc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-57349
Type: osv

## Details
The messageformat package, an implementation of the Unicode MessageFormat 2 specification for JavaScript, is vulnerable to prototype pollution due to improper handling of message key paths in versions prior to 2.3.0. The flaw arises when processing nested message keys containing special characters (e.g., __proto__ ), which can lead to unintended modification of the JavaScript Object prototype. This vulnerability may allow a remote attacker to inject properties into the global object prototype via specially crafted message input, potentially causing denial of service or other undefined behaviors in applications using the affected component.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57349.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57349
- https://github.com/messageformat/messageformat/issues/452
