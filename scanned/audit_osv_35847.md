# [C] Unverified email-based SSO account linking

## Summary
Severity: Critical
Advisory: CVE-2026-15611
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-15611
Type: osv

## Details
Logto allows unverified email-based SSO account linking, enabling an attacker to register an identity at a permissive IdP using a victim’s email and gain unauthorized access to the victim’s account.

## References
- https://github.com/logto-io/logto/blob/ea3ede35028dfd0bbb6d7b239623ce0e7f6cdff8/packages/core/src/libraries/verification-helpers/single-sign-on.ts#L274
- https://github.com/logto-io/logto/blob/ea3ede35028dfd0bbb6d7b239623ce0e7f6cdff8/packages/core/src/routes/experience/classes/verifications/enterprise-sso-verification.ts#L284-L297
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15611.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15611
