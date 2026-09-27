# [H] CVE-2023-31414

## Summary
Severity: High
Advisory: CVE-2023-31414
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-05-04
Source: https://osv.dev/vulnerability/CVE-2023-31414
Type: osv

## Details
Kibana versions 8.0.0 through 8.7.0 contain an arbitrary code execution flaw. An attacker with write access to Kibana yaml or env configuration could add a specific payload that will attempt to execute JavaScript code. This could lead to the attacker executing arbitrary commands on the host system with permissions of the Kibana process.

## References
- https://discuss.elastic.co/t/kibana-8-7-1-security-updates/332330
- https://www.elastic.co/community/security/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31414.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31414
