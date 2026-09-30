# [H] CVE-2024-34475

## Summary
Severity: High
Advisory: CVE-2024-34475
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-04
Source: https://osv.dev/vulnerability/CVE-2024-34475
Type: osv

## Details
Open5GS before 2.7.1 is vulnerable to a reachable assertion that can cause an AMF crash via NAS messages from a UE: gmm_state_authentication in amf/gmm-sm.c for != OGS_ERROR.

## References
- https://github.com/open5gs/open5gs/compare/v2.7.0...v2.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34475.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34475
- https://github.com/open5gs/open5gs/pull/3122
