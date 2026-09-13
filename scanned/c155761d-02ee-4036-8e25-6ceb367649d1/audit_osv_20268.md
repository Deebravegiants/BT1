# [M] CVE-2021-32657

## Summary
Severity: Medium
Advisory: CVE-2021-32657
Aliases: GHSA-fx62-q47f-f665
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-32657
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. In versions of Nextcloud Server prior to 10.0.11, 20.0.10, and 21.0.2, a malicious user may be able to break the user administration page. This would disallow administrators to administrate users on the Nextcloud instance. The vulnerability is fixed in versions 19.0.11, 20.0.10, and 21.0.2. As a workaround, administrators can use the OCC command line tool to administrate the Nextcloud users.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-fx62-q47f-f665
- https://hackerone.com/reports/1147611
- https://security.gentoo.org/glsa/202208-17
