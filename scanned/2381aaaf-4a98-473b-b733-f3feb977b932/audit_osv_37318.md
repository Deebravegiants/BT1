# [H] Heap-use-after-free in CIccCmm::AddXform()

## Summary
Severity: High
Advisory: CVE-2026-30978
Aliases: GHSA-97mf-f6r7-q9q4
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30978
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a heap-use-after-free in CIccCmm::AddXform() causing invalid vptr dereference and crash. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30978.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-97mf-f6r7-q9q4
- https://nvd.nist.gov/vuln/detail/CVE-2026-30978
- https://github.com/InternationalColorConsortium/iccDEV/issues/612
- https://github.com/InternationalColorConsortium/iccDEV/pull/616
