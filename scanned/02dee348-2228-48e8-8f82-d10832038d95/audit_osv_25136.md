# [C] CVE-2023-31415

## Summary
Severity: Critical
Advisory: CVE-2023-31415
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-05-04
Source: https://osv.dev/vulnerability/CVE-2023-31415
Type: osv

## Details
Kibana version 8.7.0 contains an arbitrary code execution flaw. An attacker with All privileges to the Uptime/Synthetics feature could send a request that will attempt to execute JavaScript code. This could lead to the attacker executing arbitrary commands on the host system with permissions of the Kibana process.

## References
- https://discuss.elastic.co/t/kibana-8-7-1-security-updates/332330
- https://www.elastic.co/community/security/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31415.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31415
