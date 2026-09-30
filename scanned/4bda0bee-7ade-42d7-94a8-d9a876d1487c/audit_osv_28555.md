# [M] CVE-2024-34476

## Summary
Severity: Medium
Advisory: CVE-2024-34476
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-04
Source: https://osv.dev/vulnerability/CVE-2024-34476
Type: osv

## Details
Open5GS before 2.7.1 is vulnerable to a reachable assertion that can cause an AMF crash via NAS messages from a UE: ogs_nas_encrypt in lib/nas/common/security.c for pkbuf->len.

## References
- https://github.com/open5gs/open5gs/compare/v2.7.0...v2.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34476.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34476
- https://github.com/open5gs/open5gs/pull/3122
