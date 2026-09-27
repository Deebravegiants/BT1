# [H] CVE-2024-23948

## Summary
Severity: High
Advisory: CVE-2024-23948
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2024-23948
Type: osv

## Details
Multiple improper array index validation vulnerabilities exist in the readMSH functionality of libigl v2.5.0. A specially crafted .msh file can lead to an out-of-bounds write. An attacker can provide a malicious file to trigger this vulnerability.This vulnerability concerns the `igl::MshLoader::parse_nodes` function while handling an `ascii`.msh` file.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1926
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1926
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23948.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-23948
