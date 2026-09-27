# [H] CVE-2020-11081

## Summary
Severity: High
Advisory: CVE-2020-11081
Aliases: GHSA-2xwp-8fv7-c5pm
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2020-07-10
Source: https://osv.dev/vulnerability/CVE-2020-11081
Type: osv

## Details
osquery before version 4.4.0 enables a privilege escalation vulnerability. If a Window system is configured with a PATH that contains a user-writable directory then a local user may write a zlib1.dll DLL, which osquery will attempt to load. Since osquery runs with elevated privileges this enables local escalation. This is fixed in version 4.4.0.

## References
- https://github.com/osquery/osquery/releases/tag/4.4.0
- https://github.com/osquery/osquery/security/advisories/GHSA-2xwp-8fv7-c5pm
- https://github.com/osquery/osquery/issues/6426
- https://github.com/osquery/osquery/commit/4d4957f12a6aa0becc9d01d9f97061e1e3d809c5
- https://github.com/osquery/osquery/pull/6433
