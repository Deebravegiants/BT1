# [H] Regular Expression Denial-of-Service in npm schema-inspector

## Summary
Severity: High
Advisory: GHSA-f38p-c2gq-4pmr
CVE: CVE-2021-21267
CWE: CWE-20, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-f38p-c2gq-4pmr
Type: github-advisory

## Affected
- npm: `schema-inspector` — affected >=0 <2.0.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
Email address validation is vulnerable to a denial-of-service attack where some input (for example `a@0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.`) will freeze the program or web browser page executing the code. This affects any current schema-inspector users using any version to validate email addresses. Users who do not do email validation, and instead do other types of validation (like string min or max length, etc), are not affected.

### Patches
_Has the problem been patched? What versions should users upgrade to?_
Users should upgrade to version 2.0.0, which uses a regex expression that isn't vulnerable to ReDoS. The new regex expression is more limited in what it can check, so it is more flexible than the one used before. Therefore, this was a new major version instead of a new patch version to warn people upgrading that they should make sure the email validation still works for their use case. 

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
If a user chooses to not upgrade, the only known workaround would be to stop using the email validation feature in the library. The user could, for example, accept the email address into their system but save it in a "not yet validated" state in their system until a verification email is sent to it (to determine whether the email is valid and belongs to the form submitter). Note that this is the preferred way of validating email addresses anyways.

### References
_Are there any links users can visit to find out more?_
https://gist.github.com/mattwelke/b7f42424680a57b8161794ad1737cd8f

### For more information
If you have any questions or comments about this advisory, you can create an issue in this repository.

## References
- https://github.com/schema-inspector/schema-inspector/security/advisories/GHSA-f38p-c2gq-4pmr
- https://nvd.nist.gov/vuln/detail/CVE-2021-21267
- https://gist.github.com/mattwelke/b7f42424680a57b8161794ad1737cd8f
- https://github.com/schema-inspector/schema-inspector/releases/tag/2.0.0
- https://security.netapp.com/advisory/ntap-20210528-0006
- https://www.npmjs.com/package/schema-inspector
