# [M] iccDEV: HBO in icMemDump()

## Summary
Severity: Medium
Advisory: CVE-2026-34540
Aliases: GHSA-gjx3-6cp6-q2x5
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34540
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a crafted ICC profile can trigger a heap-buffer-overflow (HBO) in icMemDump() when iccDumpProfile attempts to dump/describe malformed tag contents. The issue is observable under AddressSanitizer as an out-of-bounds heap read in icMemDump(...) at IccProfLib/IccUtil.cpp:1002, reachable via CIccTagUnknown::Describe(). This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34540.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-gjx3-6cp6-q2x5
- https://nvd.nist.gov/vuln/detail/CVE-2026-34540
- https://github.com/InternationalColorConsortium/iccDEV/issues/674
- https://github.com/InternationalColorConsortium/iccDEV/pull/689
