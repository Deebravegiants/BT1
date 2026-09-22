# [M] CVE-2022-46377

## Summary
Severity: Medium
Advisory: CVE-2022-46377
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-10
Source: https://osv.dev/vulnerability/CVE-2022-46377
Type: osv

## Details
An out-of-bounds read vulnerability exists in the PORT command parameter extraction functionality of Weston Embedded uC-FTPs v 1.98.00. A specially-crafted set of network packets can lead to denial of service. An attacker can send packets to trigger this vulnerability.This vulnerability occurs when no IP address argument is provided to the `PORT` command.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1681
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1681
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46377.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46377
- https://github.com/weston-embedded/uC-FTPs/pull/2
