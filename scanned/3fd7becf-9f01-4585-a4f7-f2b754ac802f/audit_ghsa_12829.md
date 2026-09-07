# [M] @okta/oidc-middlewareOpen Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-58h4-9m7m-j9m4
CVE: CVE-2022-3145
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-58h4-9m7m-j9m4
Type: github-advisory

## Affected
- npm: `@okta/oidc-middleware` — affected >=0 <5.0.0

## Details
An open redirect vulnerability exists in Okta OIDC Middleware prior to version 5.0.0 allowing an attacker to redirect a user to an arbitrary URL.

**Affected products and versions**
Okta OIDC Middleware prior to version 5.0.0.

**Resolution**
The vulnerability is fixed in OIDC Middleware 5.0.0.  To remediate this vulnerability, upgrade Okta OIDC Middleware to this version or later.

**CVE details**
**CVE ID:**		[CVE-2022-3145](https://cve.mitre.org/cgi-bin/cvename.cgi?name=2022-3145)
**Published Date:**	01/05/2023
**Vulnerability Type:**	Open Redirect
**CWE:**			CWE-601
**CVSS v3.1 Score:** 4.3
**Severity:** Medium
**Vector string:** AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N

**Severity Details**
To exploit this issue, an attacker would need to send a victim a malformed URL containing a target server that they control. Once a user successfully completed the login process, the victim user would then be redirected to the attacker controlled site.

**References**
https://github.com/okta/okta-oidc-middleware

## References
- https://github.com/okta/okta-oidc-middleware/security/advisories/GHSA-58h4-9m7m-j9m4
- https://nvd.nist.gov/vuln/detail/CVE-2022-3145
- https://github.com/okta/okta-oidc-middleware/commit/5d10b3ccdd5d6893de4d8b58696094267d30c113
- https://github.com/okta/okta-oidc-middleware
