# [M] CVE-2019-12794

## Summary
Severity: Medium
Advisory: CVE-2019-12794
CVSS: 6.6 (CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-11
Source: https://osv.dev/vulnerability/CVE-2019-12794
Type: osv

## Details
An issue was discovered in MISP 2.4.108. Organization admins could reset credentials for site admins (organization admins have the inherent ability to reset passwords for all of their organization's users). This, however, could be abused in a situation where the host organization of an instance creates organization admins. An organization admin could set a password manually for the site admin or simply use the API key of the site admin to impersonate them. The potential for abuse only occurs when the host organization creates lower-privilege organization admins instead of the usual site admins. Also, only organization admins of the same organization as the site admin could abuse this.

## References
- https://github.com/MISP/MISP/commit/36b43f1306873cff87b7aa30cdc1a30b38c9c16a
