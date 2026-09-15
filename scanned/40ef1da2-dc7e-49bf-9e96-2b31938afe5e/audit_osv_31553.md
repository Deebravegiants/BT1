# [M] CVE-2025-14369

## Summary
Severity: Medium
Advisory: CVE-2025-14369
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-14369
Type: osv

## Details
dr_flac, an audio decoder within the dr_libs toolset, contains an integer overflow vulnerability flaw due to trusting the totalPCMFrameCount field from FLAC metadata before calculating buffer size, allowing an attacker with a specially crafted file to perform DoS against programs using the tool.

## References
- https://www.kb.cert.org/vuls/id/924114
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14369.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14369
- https://github.com/mackron/dr_libs/commit/b2197b2eb7bb609df76315bebf44db4ec2a1aed0
