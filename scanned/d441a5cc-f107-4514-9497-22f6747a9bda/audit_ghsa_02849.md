# [H] Deleted Admin Can Sign In to Admin Interface

## Summary
Severity: High
Advisory: GHSA-6gjf-7w99-j7x7
CVE: CVE-2021-41126
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-6gjf-7w99-j7x7
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=2.1.0 <2.1.12
- Packagist: `october/system` — affected >=2.1.0 <2.1.12

## Details
### Impact
Assuming an administrator once had previous access to the admin interface, they may still be able to sign in to the backend using October CMS v2.0.

### Patches
The issue has been patched in v2.1.12

### Workarounds

- Reset the password of the deleted accounts to prevent them from signing in.

- Please contact hello@octobercms.com for code change instructions if you are unable to upgrade.

### References

Credits to:
• Daniel Bidala

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-6gjf-7w99-j7x7
- https://nvd.nist.gov/vuln/detail/CVE-2021-41126
- https://github.com/octobercms/october
- https://octobercms.com/changelog
