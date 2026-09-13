# [M] iccDEV: SO in SIccCalcOp::ArgsUsed()

## Summary
Severity: Medium
Advisory: CVE-2026-34536
Aliases: GHSA-cr68-xp9x-8597
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34536
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a crafted ICC profile can trigger a stack overflow (SO) in SIccCalcOp::ArgsUsed(). The issue is observable under AddressSanitizer as a stack-overflow when iccApplyProfiles processes a malicious profile, with the crash occurring while computing argument usage during calculator underflow/overflow checks. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34536.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-cr68-xp9x-8597
- https://nvd.nist.gov/vuln/detail/CVE-2026-34536
- https://github.com/InternationalColorConsortium/iccDEV/issues/669
- https://github.com/InternationalColorConsortium/iccDEV/pull/684
