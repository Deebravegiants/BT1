# [M] CVE-2019-13981

## Summary
Severity: Medium
Advisory: CVE-2019-13981
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-19
Source: https://osv.dev/vulnerability/CVE-2019-13981
Type: osv

## Details
In Directus 7 API through 2.3.0, remote attackers can read image files via a direct request for a filename under the uploads/_/originals/ directory. This is related to a configuration option in which the file collection can be non-public, but this option does not apply to the thumbnailer.

## References
- https://github.com/directus/api/issues/986
- https://github.com/directus/api/issues/987
