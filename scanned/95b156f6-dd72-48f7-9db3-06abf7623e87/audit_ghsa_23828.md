# [M] Cross-site Scripting in Auth0 Lock

## Summary
Severity: Medium
Advisory: GHSA-7ww6-75fj-jcj7
CVE: CVE-2022-29172
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7ww6-75fj-jcj7
Type: github-advisory

## Affected
- npm: `auth0-lock` — affected >=0 <11.33.0

## Details
### Overview

In versions before and including `11.32.2`, when the “additional signup fields” feature [is configured](https://github.com/auth0/lock#additional-sign-up-fields), a malicious actor can inject invalidated HTML code into these additional fields, which is then stored in the service `user_metdata` payload (using the `name` property).

Verification emails, when applicable, are generated using this metadata. It is therefor possible for an actor to craft a malicious link by injecting HTML, which is then rendered as the recipient's name within the delivered email template.

### Am I affected?
You are impacted by this vulnerability if you are using `auth0-lock` version `11.32.2` or lower and are using the “additional signup fields” feature in your application.

### How to fix that?
Upgrade to version `11.33.0`.

### Will this update impact my users?
Additional signup fields that have been added to the signup tab on Lock will have HTML tags stripped from user input from version `11.33.0` onwards. The user will not receive any validation warning or feedback, but backend data will no longer include HTML.

## References
- https://github.com/auth0/lock/security/advisories/GHSA-7ww6-75fj-jcj7
- https://nvd.nist.gov/vuln/detail/CVE-2022-29172
- https://github.com/auth0/lock/commit/79ae557d331274b114848150f19832ae341771b1
- https://github.com/auth0/lock
