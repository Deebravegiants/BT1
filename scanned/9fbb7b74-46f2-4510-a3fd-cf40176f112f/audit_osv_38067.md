# [M] iccDEV: UB in CIccCalculatorFunc::ApplySequence()

## Summary
Severity: Medium
Advisory: CVE-2026-34533
Aliases: GHSA-8jj3-77m7-c3pq
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34533
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a crafted ICC profile can trigger Undefined Behavior (UB) in CIccCalculatorFunc::ApplySequence() due to invalid enum values being loaded for icChannelFuncSignature. The issue is observable under UBSan as a “load of value … not a valid value for type icChannelFuncSignature”, indicating a type/enum value confusion scenario during ICC profile processing. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34533.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-8jj3-77m7-c3pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34533
- https://github.com/InternationalColorConsortium/iccDEV/issues/664
- https://github.com/InternationalColorConsortium/iccDEV/pull/681
