# [H] CVE-2024-56319

## Summary
Severity: High
Advisory: CVE-2024-56319
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-56319
Type: osv

## Details
In Matter (aka connectedhomeip or Project CHIP) through 1.4.0.0 before e3277eb, unlimited user label appends in a userlabel cluster can lead to a denial of service (resource exhaustion).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56319.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56319
- https://github.com/project-chip/connectedhomeip/issues/36760
- https://github.com/project-chip/connectedhomeip/commit/e3277eb02ed8115de5887e8beca0e35007ba71f3
- https://github.com/project-chip/connectedhomeip/pull/36843
