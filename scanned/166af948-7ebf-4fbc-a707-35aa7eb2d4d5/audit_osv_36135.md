# [M] NULL Pointer Dereference in iccDEV Unknown Tag Parser

## Summary
Severity: Medium
Advisory: CVE-2026-21497
Aliases: GHSA-7gv7-cmrv-4j85
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21497
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to NULL pointer dereference via an unknown tag parser. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21497.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-7gv7-cmrv-4j85
- https://nvd.nist.gov/vuln/detail/CVE-2026-21497
- https://github.com/InternationalColorConsortium/iccDEV/issues/374
- https://github.com/InternationalColorConsortium/iccDEV/commit/9419cac7f084197941994b8b9d17def204008385
- https://github.com/InternationalColorConsortium/iccDEV/pull/403
