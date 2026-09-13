# [C] NodeJS version of HAX CMS Has Insecure Default Configuration That Leads to Unauthenticated Access

## Summary
Severity: Critical
Advisory: GHSA-f38f-jvqj-mfg6
CVE: CVE-2025-54127
CWE: CWE-1188
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-f38f-jvqj-mfg6
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <11.0.7

## Details
### Summary
The NodeJS version of HAX CMS uses an insecure default configuration designed for local
development. The default configuration does not perform authorization or authentication checks.

### Details
If a user were to deploy haxcms-nodejs without modifying the default settings, ‘HAXCMS_DISABLE_JWT_CHECKS‘ would be set to ‘true‘ and their deployment would lack session authentication. 

![insecure-default-configuration-code](https://github.com/user-attachments/assets/af58b08a-8a26-4ef5-8deb-e6e9d4efefaa)

#### Affected Resources
- [package.json:13](https://github.com/haxtheweb/haxcms-nodejs/blob/a4d2f18341ff63ad2d97c35f9fc21af8b965248b/package.json#L13)

### PoC
To reproduce this vulnerability, [install](https://github.com/haxtheweb/haxcms-nodejs) HAX CMS NodeJS. The application will load without JWT checks enabled. 

### Impact
Without security checks in place, an unauthenticated remote attacker could access, modify, and delete all site information.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-f38f-jvqj-mfg6
- https://nvd.nist.gov/vuln/detail/CVE-2025-54127
- https://github.com/haxtheweb/haxcms-nodejs
