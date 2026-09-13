# [C] Craft CMS Remote Code Execution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4w8r-3xrw-v25g
CVE: CVE-2023-41892
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-09-13
Source: https://github.com/advisories/GHSA-4w8r-3xrw-v25g
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.4.15

## Details
### Impact

This is a high-impact, low-complexity attack vector. Users running Craft installations before 4.4.15 are encouraged to update to at least that version to mitigate the issue. 

### Mitigations

* This has been fixed in Craft 4.4.15. You should ensure you’re running at least that version.
* Refresh your security key in case it has already been captured. You can do that by running the `php craft setup/security-key` command and copying the updated `CRAFT_SECURITY_KEY` environment variable to all production environments.
* If you have any other private keys stored as environment variables (e.g., S3 or Stripe), refresh those as well.
* Out of an abundance of caution, you may want to force all your users to reset their passwords in case your database was compromised. You can do that by running `php craft resave/users --set passwordResetRequired --to "fn() => true"`.

### References

https://github.com/craftcms/cms/commit/c0a37e15cc925c473e60e27fe64054993b867ac1#diff-47dd43d86f85161944dfcce2e41d31955c4184672d9bd9d82b948c6b01b86476

https://github.com/craftcms/cms/commit/7359d18d46389ffac86c2af1e0cd59e37c298857

https://github.com/craftcms/cms/commit/a270b928f3d34ad3bd953b81c304424edd57355e

https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#4415---2023-07-03-critical

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-4w8r-3xrw-v25g
- https://nvd.nist.gov/vuln/detail/CVE-2023-41892
- https://github.com/craftcms/cms/commit/7359d18d46389ffac86c2af1e0cd59e37c298857
- https://github.com/craftcms/cms/commit/a270b928f3d34ad3bd953b81c304424edd57355e
- https://github.com/craftcms/cms/commit/c0a37e15cc925c473e60e27fe64054993b867ac1
- https://github.com/craftcms/cms/commit/c0a37e15cc925c473e60e27fe64054993b867ac1#diff-47dd43d86f85161944dfcce2e41d31955c4184672d9bd9d82b948c6b01b86476
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#4415---2023-07-03-critical
- http://packetstormsecurity.com/files/176303/Craft-CMS-4.4.14-Remote-Code-Execution.html
