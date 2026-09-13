# [M] iccDEV: UB in CIccCombinedConnectionConditions::CIccCombinedConnectionConditions()

## Summary
Severity: Medium
Advisory: CVE-2026-34541
Aliases: GHSA-9p35-7hp5-4hg4
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34541
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a crafted ICC profile can trigger Undefined Behavior (UB) via a null-pointer member call in CIccCombinedConnectionConditions::CIccCombinedConnectionConditions() (reported by UBSan as “member call on null pointer of type CIccTagSpectralViewingConditions”). The issue is reachable when running iccApplyNamedCmm with -PCC using a malformed .icc profile. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34541.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-9p35-7hp5-4hg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-34541
- https://github.com/InternationalColorConsortium/iccDEV/issues/676
- https://github.com/InternationalColorConsortium/iccDEV/pull/691
