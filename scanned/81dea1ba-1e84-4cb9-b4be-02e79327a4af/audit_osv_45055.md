# [M] PYSEC-2023-286

## Summary
Severity: Medium
Advisory: PYSEC-2023-286
Aliases: CVE-2023-50263, GHSA-75mc-3pjc-727q
Ecosystem: PyPI
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-12-12
Source: https://osv.dev/vulnerability/PYSEC-2023-286
Type: osv

## Affected
- PyPI: `nautobot` — affected >=0 <7c4cf3137f45f1541f09f2f6a7f8850cd3a2eaee, >=2.0.0 <2.0.6

## Details
Nautobot is a Network Source of Truth and Network Automation Platform built as a web application atop the Django Python framework with a PostgreSQL or MySQL database. In Nautobot 1.x and 2.0.x prior to 1.6.7 and 2.0.6, the URLs `/files/get/?name=...` and `/files/download/?name=...` are used to provide admin access to files that have been uploaded as part of a run request for a Job that has FileVar inputs. Under normal operation these files are ephemeral and are deleted once the Job in question runs. 

In the default implementation used in Nautobot, as provided by `django-db-file-storage`, these URLs do not by default require any user authentication to access; they should instead be restricted to only users who have permissions to view Nautobot's `FileProxy` model instances.

Note that no URL mechanism is provided for listing or traversal of the available file `name` values, so in practice an unauthenticated user would have to guess names to discover arbitrary files for download, but if a user knows the file name/path value, they can access it without authenticating, so we are considering this a vulnerability.

Fixes are included in Nautobot 1.6.7 and Nautobot 2.0.6. No known workarounds are available other than applying the patches included in those versions.

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-75mc-3pjc-727q
- https://github.com/nautobot/nautobot/security/advisories/GHSA-75mc-3pjc-727q
- https://github.com/nautobot/nautobot/pull/4959
- https://github.com/nautobot/nautobot/pull/4964
- https://github.com/nautobot/nautobot/commit/458280c359a4833a20da294eaf4b8d55edc91cee
- https://github.com/nautobot/nautobot/commit/7c4cf3137f45f1541f09f2f6a7f8850cd3a2eaee
- https://github.com/victor-o-silva/db_file_storage/blob/master/db_file_storage/views.py
