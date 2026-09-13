# [M] libais 0.15 - Out-of-bounds Vector Access in VdmStream::AddLine via Invalid Sequential Message ID

## Summary
Severity: Medium
Advisory: CVE-2026-56770
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-56770
Type: osv

## Details
libais through 0.15 VdmStream::AddLine uses an unchecked sentinel value as a vector index when processing AIS sentences with empty or out-of-range sequential message IDs. Remote attackers can crash services or vessel systems by sending crafted AIVDM sentences over VHF marine radio or IP feeds, causing out-of-bounds memory access and potential corruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56770.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56770
- https://www.vulncheck.com/advisories/libais-out-of-bounds-vector-access-in-vdmstream-addline-via-invalid-sequential-message-id
- https://github.com/schwehr/libais
- https://github.com/schwehr/libais/issues/263
