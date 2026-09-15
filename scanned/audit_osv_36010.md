# [M] OpenRGB: insufficient input data checks lead to Denial-of-Service, memory overread and overwrite

## Summary
Severity: Medium
Advisory: CVE-2026-18794
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-18794
Type: osv

## Details
The OpenRGB network protocol allows attackers to cause memory exhaustion and out-of-bounds memory reads and writes by passing inconsistent data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18794.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18794
- https://bugzilla.suse.com/show_bug.cgi?id=1274022
- https://gitlab.com/CalcProgrammer1/OpenRGB/-/commit/d2dd9dcc7369e78f47d01ace19af3750cd89ae66
- https://gitlab.com/CalcProgrammer1/OpenRGB
