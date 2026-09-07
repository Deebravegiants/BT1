# [H] CKAN has an XSS vector in user uploaded images in group/org and user profiles

## Summary
Severity: High
Advisory: GHSA-7pq5-qcp6-mcww
CVE: CVE-2025-24372
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-02-05
Source: https://github.com/advisories/GHSA-7pq5-qcp6-mcww
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=0 <2.10.7
- PyPI: `ckan` — affected >=2.11.0 <2.11.2

## Details
### Impact
Using a specially crafted file, a user could potentially upload a file containing code that when executed could send arbitrary requests to the server. If that file was opened by an administrator, it could lead to escalation of privileges of the original submitter or other malicious actions. Users must have been registered to the site to exploit this vulnerability.

### Patches
This vulnerability has been fixed in CKAN 2.10.7 and 2.11.2

### Workarounds
On versions prior to CKAN 2.10.7 and 2.11.2, site maintainers can restrict the file types supported for uploading using the [ckan.upload.user.mimetypes](https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-upload-user-mimetypes) / [ckan.upload.user.types](https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-upload-user-types) and [ckan.upload.group.mimetypes](https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-upload-group-mimetypes) / [ckan.upload.group.types](https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-upload-group-types) config options.
To entirely disable file uploads you can use:

```ini
ckan.upload.user.types = none
```

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-7pq5-qcp6-mcww
- https://nvd.nist.gov/vuln/detail/CVE-2025-24372
- https://github.com/ckan/ckan/commit/7da6a26c6183e0a97a356d1b1d2407f3ecc7b9c8
- https://github.com/ckan/ckan/commit/a4fc5e06634ed51d653ab819a7efc8e62f816f68
- https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-upload-group-mimetypes
- https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-upload-group-types
- https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-upload-user-mimetypes
- https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-upload-user-types
- https://github.com/ckan/ckan
