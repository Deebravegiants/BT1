# [M] wire-webapp has no database deletion on client logout

## Summary
Severity: Medium
Advisory: CVE-2025-48066
Aliases: GHSA-qc6c-2hh8-qfh8
CVSS: 6.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-48066
Type: osv

## Details
wire-webapp is the web application for the open-source messaging service Wire. A bug fix caused a regression causing an issue with function to delete local data. Instructing the client to delete its local database on user logout does not result in deletion. This is the case for both temporary clients (marking the device as a public computer on login) and regular clients instructing the deletion of all personal information and conversations upon logout. Access to the machine is required to access the data. If encryption-at-rest is used, cryptographic material can't be exported. The underlying issue has been fixed with wire-webapp version 2025-05-14-production.0. In order to mitigate potential impact, the database must be manually deleted on devices where the option "This is a public computer" was used prior to log in or a log out with the request to delete local data with the affected versions has happened before.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48066.json
- https://github.com/wireapp/wire-webapp/security/advisories/GHSA-qc6c-2hh8-qfh8
- https://nvd.nist.gov/vuln/detail/CVE-2025-48066
- https://github.com/wireapp/wire-webapp/commit/4c0ed5f1e9e0fcfceedf3c29034defce6e1fea77
