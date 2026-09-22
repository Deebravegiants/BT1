# [C] Apache Impala: SAML authentication bypass via forged bearer token

## Summary
Severity: Critical
Advisory: CVE-2026-56207
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-56207
Type: osv

## Details
Signature of Bearer token is not verified in last step of SAML2 authentication for Impala's hs2-http interface, allowing altering user name and acting as another user.



This issue affects Apache Impala: >=4.0.0.



Users are recommended to upgrade to version 4.5.2, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/09/08/22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56207.json
- https://lists.apache.org/thread/20cov78py0zqzx7dyq39ktythkwn91zs
- https://nvd.nist.gov/vuln/detail/CVE-2026-56207
