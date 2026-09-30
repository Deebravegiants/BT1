# [H] Improper Output Neutralization for Logs in Kibana Leading to Log Injection

## Summary
Severity: High
Advisory: CVE-2026-49091
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-49091
Type: osv

## Details
Improper Output Neutralization for Logs (CWE-117) in Kibana can lead to log injection via Log Injection-Tampering-Forging (CAPEC-93). An attacker can supply specially crafted input that is written to log files without proper neutralization. When the log files are subsequently viewed in a terminal that interprets control sequences, the injected content may alter the displayed log data.

## References
- https://discuss.elastic.co/t/kibana-7-17-15-8-11-1-security-update-esa-2026-53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49091.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-49091
