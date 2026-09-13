# [H] Finit bundled getty can bypass /bin/login

## Summary
Severity: High
Advisory: CVE-2025-29906
Aliases: GHSA-563g-p98j-mc9q
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2025-29906
Type: osv

## Details
Finit is a fast init for Linux systems. Versions starting from 3.0-rc1 and prior to version 4.11 bundle an implementation of getty for the `tty` configuration directive that can bypass `/bin/login`, i.e., a user can log in as any user without authentication. This issue has been patched in version 4.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29906.json
- https://github.com/troglobit/finit/security/advisories/GHSA-563g-p98j-mc9q
- https://nvd.nist.gov/vuln/detail/CVE-2025-29906
- https://github.com/troglobit/finit/commit/6528628b5c771c25ffa0cb1a46c6c89d9d0d69e0
