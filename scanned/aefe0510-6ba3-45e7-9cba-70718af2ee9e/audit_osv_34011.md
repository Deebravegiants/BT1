# [M] Open OnDemand Shell App closed websocket DoS

## Summary
Severity: Medium
Advisory: CVE-2025-53636
Aliases: GHSA-x5xv-fw37-v524
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-07-11
Source: https://osv.dev/vulnerability/CVE-2025-53636
Type: osv

## Details
Open OnDemand is an open-source HPC portal. Users can flood logs by interacting with the shell app and generating many errors. Users who flood logs can create very large log files causing a Denial of Service (DoS) to the ondemand system. This vulnerability is fixed in 3.1.14 and 4.0.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53636.json
- https://github.com/OSC/ondemand/security/advisories/GHSA-x5xv-fw37-v524
- https://nvd.nist.gov/vuln/detail/CVE-2025-53636
- https://github.com/OSC/ondemand/commit/40800d68cd019c5f1c48b2deafebba6dff4abee2
- https://github.com/OSC/ondemand/commit/96f29b995e1add7562516614e4dc8d961987e8b4
