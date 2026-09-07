# [M] @keystone-6/auth Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jqxr-vjvv-899m
CVE: CVE-2023-34247
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-jqxr-vjvv-899m
Type: github-advisory

## Affected
- npm: `@keystone-6/auth` — affected >=0 <7.0.0

## Details
### Summary
There is an open redirect in the `@keystone-6/auth` package, where the redirect leading `/` filter can be bypassed.

### Impact
Users may be redirected to domains other than the relative host, thereby it might be used by attackers to re-direct users to an unexpected location.

### Mitigations
- Don't use the `@keystone-6/auth` package

### References
- [CWE-601: URL Redirection to Untrusted Site ('Open Redirect')](https://cwe.mitre.org/data/definitions/601.html)
- [OWASP: Unvalidated Redirects and Forwards Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)

#### Similar Vulnerability Reports
- [CVE-2023-0748](https://nvd.nist.gov/vuln/detail/CVE-2023-0748)
- [CVE-2022-2252](https://nvd.nist.gov/vuln/detail/CVE-2022-2252)

#### Credits
Thanks to [morioka12](https://github.com/scgajge12) for reporting this problem.

If you have any questions around this security advisory, please don't hesitate to contact us at [security@keystonejs.com](mailto:security@keystonejs.com), or [open an issue on GitHub](https://github.com/keystonejs/keystone/issues/new/choose).

If you have a security flaw to report for any software in this repository, please see our [SECURITY policy](https://github.com/keystonejs/keystone/blob/main/SECURITY.md).

## References
- https://github.com/keystonejs/keystone/security/advisories/GHSA-jqxr-vjvv-899m
- https://nvd.nist.gov/vuln/detail/CVE-2023-34247
- https://github.com/keystonejs/keystone/pull/8626
- https://github.com/keystonejs/keystone
