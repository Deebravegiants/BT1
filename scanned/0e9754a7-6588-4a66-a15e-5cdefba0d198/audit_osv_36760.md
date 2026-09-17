# [H] iccDEV memcpy-param-overlap in CIccTagMultiProcessElement::Apply()

## Summary
Severity: High
Advisory: CVE-2026-25634
Aliases: GHSA-35rg-jcmp-583h
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-25634
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to 2.3.1.4, SrcPixel and DestPixel stack buffers overlap in CIccTagMultiProcessElement::Apply() int IccTagMPE.cpp. This vulnerability is fixed in 2.3.1.4.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25634.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-35rg-jcmp-583h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25634
- https://github.com/InternationalColorConsortium/iccDEV/issues/577
- https://github.com/InternationalColorConsortium/iccDEV/commit/9206e0b8684e4cf4186d9ae768f16760bc1af9ff
- https://github.com/InternationalColorConsortium/iccDEV/pull/579
