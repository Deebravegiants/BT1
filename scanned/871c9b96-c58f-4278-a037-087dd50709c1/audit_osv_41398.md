# [C] Apache Answer: Residual Administrative API Key Access After Role or Account Revocation

## Summary
Severity: Critical
Advisory: CVE-2026-60053
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-60053
Type: osv

## Details
Insufficient Session Expiration vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.1.

Administrative API keys remained usable after the owning administrator was demoted or the account was marked inactive, suspended, or deleted, allowing continued access until the keys were explicitly removed.
Users are recommended to upgrade to version 2.0.2, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/05/14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60053.json
- https://lists.apache.org/thread/2vkcj3bdvso6cywnklt2vtkc2m4o0b5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-60053
