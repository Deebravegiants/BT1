# [C] NixOs Odoo database and filestore publicly accessible with default odoo configuration

## Summary
Severity: Critical
Advisory: CVE-2026-25137
Aliases: GHSA-cwmq-6wv5-f3px
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-02-02
Source: https://osv.dev/vulnerability/CVE-2026-25137
Type: osv

## Details
The NixOs Odoo package is an open source ERP and CRM system. From 21.11 to before 25.11 and 26.05, every NixOS based Odoo setup publicly exposes the database manager without any authentication. This allows unauthorized actors to delete and download the entire database, including Odoos file store. Unauthorized access is evident from http requests. If kept, searching access logs and/or Odoos log for requests to /web/database can give indicators, if this has been actively exploited. The database manager is a featured intended for development and not meant to be publicly reachable. On other setups, a master password acts as 2nd line of defence. However, due to the nature of NixOS, Odoo is not able to modify its own configuration file and thus unable to persist the auto-generated password. This also applies when manually setting a master password in the web-UI. This means, the password is lost when restarting Odoo. When no password is set, the user is prompted to set one directly via the database manager. This requires no authentication or action by any authorized user or the system administrator. Thus, the database is effectively world readable by anyone able to reach Odoo. This vulnerability is fixed in 25.11 and 26.05.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25137.json
- https://github.com/NixOS/nixpkgs/security/advisories/GHSA-cwmq-6wv5-f3px
- https://nvd.nist.gov/vuln/detail/CVE-2026-25137
- https://github.com/NixOS/nixpkgs/pull/485310
- https://github.com/NixOS/nixpkgs/pull/485454
