# [M] CVE-2024-51406

## Summary
Severity: Medium
Advisory: CVE-2024-51406
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-01
Source: https://osv.dev/vulnerability/CVE-2024-51406
Type: osv

## Details
Floodlight SDN Open Flow Controller v.1.2 has an issue that allows local hosts to build fake LLDP packets that allow specific clusters to be missed by Floodlight, which in turn leads to missed hosts inside and outside the cluster.

## References
- https://ieeexplore.ieee.org/document/10246976
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51406.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-51406
- https://github.com/floodlight/floodlight/issues/870
- https://github.com/floodlight/floodlight
