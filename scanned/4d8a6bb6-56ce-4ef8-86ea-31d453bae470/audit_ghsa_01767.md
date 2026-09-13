# [H] Remote Code Execution Through Image Uploads in BookStack

## Summary
Severity: High
Advisory: GHSA-g9rq-x4fj-f5hx
CVE: CVE-2020-5256
CWE: CWE-95
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2020-03-13
Source: https://github.com/advisories/GHSA-g9rq-x4fj-f5hx
Type: github-advisory

## Affected
- Packagist: `ssddanbrown/bookstack` — affected >=0 <0.25.5

## Details
### Impact

A user could upload PHP files through image upload functions, which would allow them to execute code on the host system remotely. They would then have the permissions of the PHP process.

This most impacts scenarios where non-trusted users are given permission to upload images in any area of the application. 

### Patches

The issue was addressed in a series of patches: v0.25.3, v0.25.4 and v0.25.5.
Users should upgrade to at least v0.25.5 to avoid this patch but ideally the latest BookStack version as previous versions are un-supported.

### Workarounds

Depending on BookStack version, you could use the [local_secure](https://www.bookstackapp.com/docs/admin/upload-config/#local-secure) image storage option, or use s3 or a similar compatible service.

Preventing direct execution of any `php` files, apart from the `public/index.php` file, though web-server configuration would also prevent this.

### References

[BookStack Beta v0.25.3](https://github.com/BookStackApp/BookStack/releases/tag/v0.25.3)
[BookStack Beta v0.25.4](https://github.com/BookStackApp/BookStack/releases/tag/v0.25.4)
[BookStack Beta v0.25.5](https://github.com/BookStackApp/BookStack/releases/tag/v0.25.5)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [the BookStack GitHub repository](BookStackApp/BookStack/issues).
* Ask on the [BookStack Discord chat](https://discord.gg/ztkBqR2).
* Follow the [BookStack Security advise](https://github.com/BookStackApp/BookStack#-security) to contact someone privately.

## References
- https://github.com/BookStackApp/BookStack/security/advisories/GHSA-g9rq-x4fj-f5hx
- https://nvd.nist.gov/vuln/detail/CVE-2020-5256
- https://github.com/BookStackApp/BookStack/releases/tag/v0.25.3
- https://github.com/BookStackApp/BookStack/releases/tag/v0.25.4
- https://github.com/BookStackApp/BookStack/releases/tag/v0.25.5
