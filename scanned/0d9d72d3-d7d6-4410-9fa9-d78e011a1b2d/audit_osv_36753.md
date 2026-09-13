# [H] iccDEV vulnerable to Stack-based Buffer Overflow in CIccTagFloatNum::GetValues()

## Summary
Severity: High
Advisory: CVE-2026-25584
Aliases: GHSA-xjr3-v3vr-5794
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25584
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.3, there is a stack-buffer-overflow vulnerability in CIccTagFloatNum<>::GetValues(). This is triggered when processing a malformed ICC profile. The vulnerability allows an out-of-bounds write on the stack, potentially leading to memory corruption, information disclosure, or code execution when processing specially crafted ICC files. This issue has been patched in version 2.3.1.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25584.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-xjr3-v3vr-5794
- https://nvd.nist.gov/vuln/detail/CVE-2026-25584
- https://github.com/InternationalColorConsortium/iccDEV/issues/551
- https://github.com/InternationalColorConsortium/iccDEV/commit/c9cb108f58683bd87afca616dea3e4cdb884c23f
- https://github.com/InternationalColorConsortium/iccDEV/pull/565
