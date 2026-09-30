# [M] CVE-2020-26273

## Summary
Severity: Medium
Advisory: CVE-2020-26273
Aliases: GHSA-4g56-2482-x7q8
CVSS: 5.2 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2020-12-16
Source: https://osv.dev/vulnerability/CVE-2020-26273
Type: osv

## Details
osquery is a SQL powered operating system instrumentation, monitoring, and analytics framework. In osquery before version 4.6.0, by using sqlite's ATTACH verb, someone with administrative access to osquery can cause reads and writes to arbitrary sqlite databases on disk. This _does_ allow arbitrary files to be created, but they will be sqlite databases. It does not appear to allow existing non-sqlite files to be overwritten. This has been patched in osquery 4.6.0. There are several mitigating factors and possible workarounds. In some deployments, the people with access to these interfaces may be considered administrators. In some deployments, configuration is managed by a central tool. This tool can filter for the `ATTACH` keyword. osquery can be run as non-root user. Because this also limits the desired access levels, this requires deployment specific testing and configuration.

## References
- https://github.com/osquery/osquery/releases/tag/4.6.0
- https://github.com/osquery/osquery/commit/c3f9a3dae22d43ed3b4f6a403cbf89da4cba7c3c
- https://github.com/osquery/osquery/security/advisories/GHSA-4g56-2482-x7q8
- https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/SQLite%20Injection.md#remote-command-execution-using-sqlite-command---load_extension
