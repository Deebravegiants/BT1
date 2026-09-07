# [C] rdiffweb vulnerable to account access via session fixation

## Summary
Severity: Critical
Advisory: GHSA-j3q4-gmj4-mj95
CVE: CVE-2022-3269
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-j3q4-gmj4-mj95
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.7

## Details
rdiffweb prior to 2.4.7 fails to invalidate session cookies on logout, leading to session fixation and allowing an attacker to access a users account. After logging in and logging out, the application continues to use the preauthentication cookies. The cookies remain the same after closing the browser and after password reset. The same cookies are reassigned for additional user logins which can lead to session fixation. An attacker can gain unauthorized access to the account of users who are using the same browser as long as a single session cookie persists on that browser once the attacker obtains a session cookie through another attack. This issue is patched in version 2.4.7. There are no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3269
- https://github.com/ikus060/rdiffweb/commit/39e7dcd4a1f44d2a7bd92b79d78a800910b1b22b
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-290.yaml
- https://huntr.dev/bounties/67c25969-5e7a-4424-817e-e1a918f63cc6
