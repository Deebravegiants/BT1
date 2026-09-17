# [M] iccDEV: SEGV in CIccTagArray::Cleanup()

## Summary
Severity: Medium
Advisory: CVE-2026-34535
Aliases: GHSA-965q-9pp6-6vw5
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34535
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a crafted ICC profile can trigger a segmentation fault (SEGV) in CIccTagArray::Cleanup(). The issue is observable under UBSan/ASan as misaligned member access / misaligned pointer loads followed by an invalid read leading to process crash when running iccRoundTrip on a malicious profile. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34535.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-965q-9pp6-6vw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-34535
- https://github.com/InternationalColorConsortium/iccDEV/issues/666
- https://github.com/InternationalColorConsortium/iccDEV/pull/683
