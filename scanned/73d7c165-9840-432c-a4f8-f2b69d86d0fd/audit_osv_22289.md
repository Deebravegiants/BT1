# [C] Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') in django-s3file

## Summary
Severity: Critical
Advisory: CVE-2022-24840
Aliases: GHSA-4w8f-hjm9-xwgf, PYSEC-2022-208
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-06-06
Source: https://osv.dev/vulnerability/CVE-2022-24840
Type: osv

## Details
django-s3file is a lightweight file upload input for Django and Amazon S3 . In versions prior to 5.5.1 it was possible to traverse the entire AWS S3 bucket and in most cases to access or delete files. If the `AWS_LOCATION` setting was set, traversal was limited to that location only. The issue was discovered by the maintainer. There were no reports of the vulnerability being known to or exploited by a third party, prior to the release of the patch. The vulnerability has been fixed in version 5.5.1 and above. There is no feasible workaround. We must urge all users to immediately updated to a patched version.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24840.json
- https://github.com/codingjoe/django-s3file/security/advisories/GHSA-4w8f-hjm9-xwgf
- https://nvd.nist.gov/vuln/detail/CVE-2022-24840
- https://github.com/codingjoe/django-s3file/commit/68ccd2c621a40eb66fdd6af2be9d5fcc9c373318
