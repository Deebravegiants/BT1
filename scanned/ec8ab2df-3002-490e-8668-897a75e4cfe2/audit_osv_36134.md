# [M] NULL Pointer Dereference in iccDEV Signature Parser

## Summary
Severity: Medium
Advisory: CVE-2026-21496
Aliases: GHSA-wj8m-6w77-r4rw
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21496
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to NULL pointer dereference via the signature parser. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21496.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-wj8m-6w77-r4rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-21496
- https://github.com/InternationalColorConsortium/iccDEV/issues/381
- https://github.com/InternationalColorConsortium/iccDEV/commit/0e51ceb427925b7e22f0465547df7506d35cda1c
- https://github.com/InternationalColorConsortium/iccDEV/commit/b5ad23aceece3789bdf1c47bae1ecf9d7bfcd26d
- https://github.com/InternationalColorConsortium/iccDEV/pull/405
