# [H] Craft CMS has a potential RCE with a compromised security key

## Summary
Severity: High
Advisory: GHSA-x684-96hh-833x
CVE: CVE-2025-23209
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-x684-96hh-833x
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.5.8
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.13.8

## Details
### Impact

This is an RCE vulnerability that affects Craft 4 and 5 installs where your security key has already been compromised.

https://craftcms.com/knowledge-base/securing-craft#keep-your-secrets-secret

Anyone running an unpatched version of Craft with a compromised security key is affected.

### Patches

This has been patched in Craft 5.5.8 and 4.13.8.

### Workarounds

If you can't update to a patched version, then rotating your security key and ensuring its privacy will help to migitgate the issue.

### References

https://github.com/craftcms/cms/commit/e59e22b30c9dd39e5e2c7fe02c147bcbd004e603

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-x684-96hh-833x
- https://nvd.nist.gov/vuln/detail/CVE-2025-23209
- https://github.com/craftcms/cms/commit/e59e22b30c9dd39e5e2c7fe02c147bcbd004e603
- https://craftcms.com/knowledge-base/securing-craft#keep-your-secrets-secret
- https://github.com/craftcms/cms
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-23209
