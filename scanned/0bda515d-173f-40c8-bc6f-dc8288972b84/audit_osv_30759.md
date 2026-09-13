# [H] CVE-2024-56318

## Summary
Severity: High
Advisory: CVE-2024-56318
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-56318
Type: osv

## Details
In raw\TCP.cpp in Matter (aka connectedhomeip or Project CHIP) through 1.4.0.0 before 27ca6ec, there is a NULL pointer dereference in TCPBase::ProcessSingleMessage via TCP packets with zero messageSize, leading to denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56318.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56318
- https://github.com/project-chip/connectedhomeip/issues/36750
- https://github.com/project-chip/connectedhomeip/commit/27ca6ec255b78168e04bd71e0f1a473869cf144b
- https://github.com/project-chip/connectedhomeip/pull/36751
