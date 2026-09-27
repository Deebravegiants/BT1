# [H] CVE-2025-29339

## Summary
Severity: High
Advisory: CVE-2025-29339
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-22
Source: https://osv.dev/vulnerability/CVE-2025-29339
Type: osv

## Details
An issue in UPF in Open5GS UPF versions up to v2.7.2 results an assertion failure vulnerability in PFCP session parameter validation. When processing a PFCP Session Establishment Request with PDN Type=0, the UPF fails to handle the invalid value propagated from SMF (or via direct attack), triggering a fatal assertion check and causing a daemon crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29339.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-29339
- https://github.com/open5gs/open5gs/issues/3727
