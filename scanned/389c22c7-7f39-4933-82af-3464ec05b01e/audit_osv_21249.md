# [M] CVE-2021-41325

## Summary
Severity: Medium
Advisory: CVE-2021-41325
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-09-30
Source: https://osv.dev/vulnerability/CVE-2021-41325
Type: osv

## Details
Broken access control for user creation in Pydio Cells 2.2.9 allows remote anonymous users to create standard users via the profile parameter. (In addition, such users can be granted several admin permissions via the Roles parameter.)

## References
- https://charonv.net/Pydio-Broken-Access-Control/
- https://github.com/pydio/cells/releases/tag/v2.2.12
- https://pydio.com/fr/community/releases/pydio-cells/pydio-cells-enterprise-2212
