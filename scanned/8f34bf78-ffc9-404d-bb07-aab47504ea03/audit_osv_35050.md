# [M] EVerest's inadequate exception handling leads to denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-68135
Aliases: GHSA-g7mm-r6qp-96vh
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-68135
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2025.10.0, C++ exceptions are not properly handled for and by the `TbdController` loop, leading to its caller and itself to silently terminates. Thus, this leads to a denial of service as it is responsible of SDP and ISO15118-20 servers. Version 2025.10.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68135.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-g7mm-r6qp-96vh
- https://nvd.nist.gov/vuln/detail/CVE-2025-68135
