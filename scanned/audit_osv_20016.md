# [H] CVE-2021-29439

## Summary
Severity: High
Advisory: CVE-2021-29439
Aliases: GHSA-wg37-cf5x-55hq
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-13
Source: https://osv.dev/vulnerability/CVE-2021-29439
Type: osv

## Details
The Grav admin plugin prior to version 1.10.11 does not correctly verify caller's privileges. As a consequence, users with the permission `admin.login` can install third-party plugins and their dependencies. By installing the right plugin, an attacker can obtain an arbitrary code execution primitive and elevate their privileges on the instance. The vulnerability has been addressed in version 1.10.11. As a mitigation blocking access to the `/admin` path from untrusted sources will reduce the probability of exploitation.

## References
- https://github.com/getgrav/grav-plugin-admin/security/advisories/GHSA-wg37-cf5x-55hq
- https://github.com/getgrav/grav-plugin-admin/commit/a220359877fd1281f76ba732e5308e0e3002e4b1
