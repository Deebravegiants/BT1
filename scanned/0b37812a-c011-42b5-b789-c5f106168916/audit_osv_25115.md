# [C] effectindex/tripreporter vulnerable to improper password verification on POST `/api/v1/account/login`

## Summary
Severity: Critical
Advisory: CVE-2023-31123
Aliases: GHSA-356r-rwp8-h6m6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-05-08
Source: https://osv.dev/vulnerability/CVE-2023-31123
Type: osv

## Details
`effectindex/tripreporter` is a community-powered, universal platform for submitting and analyzing trip reports. Prior to commit bd80ba833b9023d39ca22e29874296c8729dd53b, any user with an account on an instance of `effectindex/tripreporter`, e.g. `subjective.report`, may be affected by an improper password verification vulnerability. The vulnerability allows any user with a password matching the password requirements to log in as any user. This allows access to accounts / data loss of the user. This issue is patched in commit bd80ba833b9023d39ca22e29874296c8729dd53b. No action necessary for users of `subjective.report`, and anyone running their own instance should update to this commit or newer as soon as possible. As a workaround, someone running their own instance may apply the patch manually.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31123.json
- https://github.com/effectindex/tripreporter/security/advisories/GHSA-356r-rwp8-h6m6
- https://nvd.nist.gov/vuln/detail/CVE-2023-31123
- https://github.com/effectindex/tripreporter/commit/bd80ba833b9023d39ca22e29874296c8729dd53b
