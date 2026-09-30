# [H] CVE-2022-41985

## Summary
Severity: High
Advisory: CVE-2022-41985
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-05-10
Source: https://osv.dev/vulnerability/CVE-2022-41985
Type: osv

## Details
An authentication bypass vulnerability exists in the Authentication functionality of Weston Embedded uC-FTPs v 1.98.00. A specially crafted set of network packets can lead to authentication bypass and denial of service. An attacker can send a sequence of unauthenticated packets to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1680
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1680
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41985.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41985
- https://github.com/weston-embedded/uC-FTPs/pull/1
