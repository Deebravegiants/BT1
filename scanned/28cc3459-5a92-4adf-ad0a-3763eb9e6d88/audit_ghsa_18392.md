# [H] NodeJS version of the HAX CMS application is distributed with Default Secrets

## Summary
Severity: High
Advisory: GHSA-5fpv-5qvh-7cf3
CVE: CVE-2025-54137
CWE: CWE-1392
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-5fpv-5qvh-7cf3
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <11.0.10

## Details
### Summary

The NodeJS version of the HAX CMS application is distributed with hardcoded default credentials for the user and superuser accounts. Additionally, the application has default private keys for JWTs. Users aren't prompted to change credentials or secrets during installation, and there is no way to change them through the UI.

### Affected Resources

- [HAXCMS.js](https://github.com/haxtheweb/haxcms-nodejs/blob/main/src/lib/HAXCMS.js#L1614) HAXCMSClass

### Impact

An unauthenticated attacker can read the default user credentials and JWT private keys from the public haxtheweb GitHub repositories. These credentials and keys can be used to access unconfigured self-hosted instances of the application, modify sites, and perform further attacks.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-5fpv-5qvh-7cf3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54137
- https://github.com/haxtheweb/haxcms-nodejs/commit/6dc2441c876350ca6fe9fbaecb058d92ef442869
- https://github.com/haxtheweb/haxcms-nodejs/blob/main/src/lib/HAXCMS.js#L1614
- https://github.com/haxtheweb/issues
