# [M] Authelia allows open redirects on the logout endpoint

## Summary
Severity: Medium
Advisory: GHSA-36f2-fcrx-fp4j
CVE: CVE-2021-29456
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-16
Source: https://github.com/advisories/GHSA-36f2-fcrx-fp4j
Type: github-advisory

## Affected
- Go: `github.com/authelia/authelia/v4` — affected >=0 <4.28.0

## Details
### Impact
Utilizing a HTTP query parameter an attacker is able to redirect users from the web application to any domain. The URL of the intended redirect should always be checked for safety prior to forwarding the user. Other endpoints of the web application already do this, they check both that the domain is using the HTTPS protocol and that it exists on a domain associated with the application.

An attacker is able to use this unintended functionality to redirect users to malicious sites. This particular security issue allows the attacker to make a phishing attempt seem much more trustworthy to a user of the web application as the initial site before redirection is familiar to them, as well as the actual URL which they have theoretically visited frequently. 

While this security issue does not directly impact the security of the web application, it is still not an acceptable scenario for the reasons mentioned above. 

### Patches
f0cb75e1e102f95f91e9254c66c797e821857690 fix(handlers): logout redirection validation (#1908) [v4.28.0](https://github.com/authelia/authelia/releases/tag/v4.28.0)

### Workarounds
Using a reverse proxy to strip the query parameter from the affected endpoint. 

### References
https://github.com/authelia/authelia/pull/1908

[CWE-601](https://cwe.mitre.org/data/definitions/601.html)

[Authelia v4.28.0](https://github.com/authelia/authelia/tree/v4.28.0)

### For more information
If you have any questions or comments about this advisory, please [contact us](https://github.com/authelia/authelia#contact-options). You may also contact us to request creating a back-ported fix for this if you are able to explain why you cannot upgrade; however upgrading is highly preferable.

## References
- https://github.com/authelia/authelia/security/advisories/GHSA-36f2-fcrx-fp4j
- https://nvd.nist.gov/vuln/detail/CVE-2021-29456
- https://github.com/authelia/authelia
