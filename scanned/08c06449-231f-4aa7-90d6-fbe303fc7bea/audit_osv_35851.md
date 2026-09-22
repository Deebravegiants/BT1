# [C] Local MFA not enforced during SSO sign-in

## Summary
Severity: Critical
Advisory: CVE-2026-15616
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-15616
Type: osv

## Details
Logto does not enforce locally configured MFA during SSO authentication, allowing users to bypass second-factor requirements and grants unauthorized access.

## References
- https://github.com/logto-io/logto/blob/ea3ede35028dfd0bbb6d7b239623ce0e7f6cdff8/packages/core/src/routes/experience/classes/experience-interaction.ts#L538-L540
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15616.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15616
